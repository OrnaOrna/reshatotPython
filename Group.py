class Group:
    groupName = None
    groupID = None
    password = None
    members = []
    namesMem = []

    def __init__(self,groupName,groupID,password):
        self.groupName = groupName
        self.groupID = groupID
        self.password = password



