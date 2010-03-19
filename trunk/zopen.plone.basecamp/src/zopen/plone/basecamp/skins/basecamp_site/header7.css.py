context.REQUEST.RESPONSE.setHeader('content-type', 'text/css')
return getattr(context, 'header.css')(context, context.REQUEST)

