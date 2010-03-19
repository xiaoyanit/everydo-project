userid = context.portal_membership.getAuthenticatedMember().getMemberId()
results = context.portal_catalog(portal_type="Person", getId=userid)
if results:
    emp = results[0].getObject()
    return context.REQUEST.RESPONSE.redirect(emp.absolute_url() + '/base_edit')
else:
    return context.REQUEST.RESPONSE.redirect('personalize_form')
