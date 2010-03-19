def expandPath(self):
    request = self.REQUEST
    username = request.HTTP_HOST.split('.')[0]
    TraversalRequestNameStack.insert(0, 'pages')
    TraversalRequestNameStack.insert(0, username)
    TraversalRequestNameStack.insert(0, 'people')
    return request

