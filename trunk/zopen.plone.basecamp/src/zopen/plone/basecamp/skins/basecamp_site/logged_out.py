home_url = context.portal_url()
context.REQUEST.RESPONSE.redirect(home_url + '/login_form')
