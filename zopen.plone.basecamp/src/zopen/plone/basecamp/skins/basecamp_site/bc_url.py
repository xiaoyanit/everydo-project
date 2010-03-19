type_name = context.portal_type # getPortalTypeName()

if hasattr(context, 'getURL'):
    obj_url = context.getURL()
    obj_id = context.getId
else:
    obj_url = context.absolute_url()
    obj_id = context.getId()

if type_name in ['Image', 'File']:
    return '%s/@@file_view' % obj_url
elif type_name == 'Discussion Item':
    return '%s/../../view#%s' % (obj_url, obj_id)
elif type_name == 'Comment':
    return '%s/..#%s' % (obj_url, obj_id)
elif type_name == 'TodoItem':
    return '%s/@@todoitem_view' % (obj_url)
elif type_name == 'Milestone':
    return '%s/..#%s' % (obj_url, obj_id)
else:
    return obj_url

