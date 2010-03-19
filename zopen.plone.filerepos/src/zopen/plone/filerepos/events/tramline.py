def notifyFRSToRemove(ob, event):
    """ tell apache to remove stuff in frs"""
    try:
        resp = event.oldParent.REQUEST.RESPONSE
    except AttributeError:
        # 避免创建站点的时候失败
        return

    path = '/'.join(ob.getPhysicalPath())
    path_s = path + '/'

    # 是否是删除第一个对象
    existing_paths = resp.getHeader('tramline_remove') 

    if existing_paths:
        existing_paths = existing_paths.split(':')
    else:
        existing_paths = []

    # 合并需要删除的文件夹 (父文件夹删除后，子文件夹就不需要再次删除)
    to_remove = []
    for e_path in existing_paths:
        if (e_path+'/').startswith(path_s):
            to_remove.append(e_path)
            continue
        elif path_s.startswith(e_path + '/'):
            return

    for p in to_remove:
        existing_paths.remove(p)
    existing_paths.append(path)
    resp.setHeader('tramline_remove', ':'.join(existing_paths))

def notifyFRSToMove(ob, event):
    """ """
    if event.oldParent is None or event.newParent is None:
        # ObjectAddEvent
        return

    resp = event.oldParent.REQUEST.RESPONSE
    id = ob.getId()

    from_path = '/'.join(event.oldParent.getPhysicalPath()) + '/' + id
    to_path = '/'.join(event.newParent.getPhysicalPath()) + '/' + id

    existing_paths = resp.getHeader('tramline_move') 
    paths = existing_paths and existing_paths + '|' or ''

    paths += from_path + ':' + to_path

    # XXX 合并优化？

    resp.setHeader('tramline_move', paths)

