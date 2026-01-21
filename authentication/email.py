
import os.path
import re
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart
from email import encoders


class EmailMultiRelated(EmailMultiAlternatives):
    """
    A version of EmailMessage that makes it easy to send multipart/related
    messages. For example, including text and HTML versions with inline images.
    @see https://djangosnippets.org/snippets/2215/
    """
    related_subtype = 'related'

    def __init__(self, *args, **kwargs):
        self.related_attachments = []
        super(EmailMultiRelated, self).__init__(*args, **kwargs)

    def attach_related(self, filename=None, content=None, mimetype=None):
        """Attaches a file with the given filename and content."""
        if isinstance(filename, MIMEBase):
            assert content == mimetype == None
            self.related_attachments.append(filename)
        else:
            assert content is not None
            self.related_attachments.append((filename, content, mimetype))

    def attach_related_file(self, path, mimetype=None):
        """Attaches a file from the filesystem."""
        filename = os.path.basename(path)
        with open(path, 'rb') as f:
            content = f.read()
        self.attach_related(filename, content, mimetype)

    def _create_message(self, msg):
        return self._create_attachments(
            self._create_related_attachments(
                self._create_alternatives(msg)
            )
        )

    def _create_alternatives(self, msg):
        """Replaces references to related attachments in HTML alternatives"""
        for i, alternative in enumerate(self.alternatives):
            if hasattr(alternative, 'content'):
                content = alternative.content
                mimetype = alternative.mimetype
            else:
                content, mimetype = alternative

            if mimetype == 'text/html':
                for attachment in self.related_attachments:
                    if isinstance(attachment, MIMEBase):
                        content_id = attachment.get('Content-ID')
                        if content_id:
                            content_id = content_id.strip('<>')
                            content = re.sub(
                                r'(?<!cid:)%s' % re.escape(content_id),
                                'cid:%s' % content_id,
                                content
                            )
                    else:
                        filename, _, _ = attachment
                        content = re.sub(
                            r'(?<!cid:)%s' % re.escape(filename),
                            'cid:%s' % filename,
                            content
                        )

                if hasattr(self.alternatives[i], 'content'):
                    from collections import namedtuple
                    Alternative = namedtuple('Alternative', ['content', 'mimetype'])
                    self.alternatives[i] = Alternative(content, mimetype)
                else:
                    self.alternatives[i] = (content, mimetype)

        return super(EmailMultiRelated, self)._create_alternatives(msg)

    def _create_related_attachments(self, msg):
        encoding = self.encoding or settings.DEFAULT_CHARSET
        if self.related_attachments:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.related_subtype, encoding=encoding)
            if self.body:
                msg.attach(body_msg)
            for attachment in self.related_attachments:
                if isinstance(attachment, MIMEBase):
                    msg.attach(attachment)
                else:
                    msg.attach(self._create_related_attachment(*attachment))
        return msg

    def _create_related_attachment(self, filename, content, mimetype=None):
        """
        Convert the filename, content, mimetype triple into a MIME attachment
        object. Use Content-ID for inline images.
        """
        if mimetype is None:
            mimetype = 'application/octet-stream'

        if '/' in mimetype:
            basetype, subtype = mimetype.split('/', 1)
        else:
            basetype = mimetype
            subtype = 'octet-stream'

        if basetype == 'image':
            attachment = MIMEImage(content, _subtype=subtype)
        elif basetype == 'text':
            from email.mime.text import MIMEText
            attachment = MIMEText(content.decode('utf-8'), _subtype=subtype)
        else:
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(content)
            encoders.encode_base64(attachment)


        if filename:
            attachment.add_header('Content-Disposition', 'inline', filename=filename)
            attachment.add_header('Content-ID', '<%s>' % filename)

        return attachment



