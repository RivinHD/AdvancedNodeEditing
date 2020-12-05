import bpy

def checkExist(Name, ANE):
    if bpy.context.object.active_material.node_tree.nodes.find(Name) != -1:
        return True
    else:
        ANE.MainNode = ""
        ANE.MainLabel = ""
        return False

def getDistances(nodes, index):
    l = [0]
    for i in range(len(nodes) - 1):
        l.append(nodes[i].location[index] - nodes[i].dimensions[index] - nodes[i + 1].location[index])
    return l

def sortNodeLocation(nodes):
    if len(nodes) <= 0:
        return
    nodes = list(dict.fromkeys(nodes))
    nodesLoc = sortByLocation(nodes, 1, True)
    nodesDistances = getDistances(nodesLoc, 1)
    loc = nodesLoc[0].location[1]
    nodes[0].location[1] = loc
    for i in range(1, len(nodesLoc)):
        loc -= nodes[i - 1].dimensions[1] + nodesDistances[i]
        nodes[i].location[1] = loc

def getGroupPorts(nodes, port):
    groupType = "GROUP_" + port
    for node in nodes:
        if node.type == groupType:
            return node

def getSelected(nodes, exclude = None):
    l = []
    for node in nodes:
        if node.select and node.name != exclude:
            l.append(node)
    return l

def sortByLocation(nodes, index, reverse):
    return sorted(nodes, key=lambda x: (x.location[index], x.name), reverse= reverse)

def getLow(nodes, index):
    low = nodes[0].location[index] - index * nodes[0].dimensions[index]
    for node in nodes[1:]:
        checkLow = node.location[index] - index * node.dimensions[index]
        if checkLow < low:
            low = checkLow
    return low

def getHeigh(nodes, index):
    high = nodes[0].location[index] + (1 - index) * nodes[0].dimensions[index]
    for node in nodes[1:]:
        checkHigh = node.location[index] + (1 - index) * node.dimensions[index]
        if checkHigh > high:
            high = checkHigh
    return high 

def checkFit(nodes, index, distance):
    for node in nodes:
        distance -= node.dimensions[index]
    return (distance >= 0, distance) 

def distribute(selected, index):
    selected = sortByLocation(selected, index, True)
    heigh = getHeigh(selected, index)
    low = getLow(selected, index)
    check, space = checkFit(selected, index, heigh - low)
    if check:
        singleSpace = space/(len(selected) - 1)
        loc = selected[0].location[index]
        for node in selected:
            node.location[index] = loc
            loc -= node.dimensions[index] + singleSpace
    else:
        loc = selected[0].location[index] + space * -0.5
        for node in selected:
            node.location[index] = loc
            loc -= node.dimensions[index]

def getPort(active):
    if active.active_output != -1:
        index = active.active_output
        socketTyp = active.outputs
    elif active.active_input != -1:
        index = active.active_input
        socketTyp = active.inputs
    return (socketTyp[index], socketTyp, index)

def findNodeOfSocket(nodes, Type):
    for node in nodes:
        if node.type == 'GROUP_' + Type:
            return node

def getDefaultSocket(active, port, index):
    portType = 'OUTPUT' if port.is_output else 'INPUT'
    node = findNodeOfSocket(active.nodes, portType)
    if portType == 'OUTPUT':
        nodePort = node.inputs[index]
    else:
        nodePort = node.outputs[index]
    return nodePort.bl_idname

def find_node_input(nodes):
    for node in nodes:
        if node.bl_idname == "NodeGroupInput":
            return node
    raise ValueError("No NodeGroupInput.")

def get_terminal_to_sockets(to_socket) -> []:
    if to_socket.node.bl_idname != "NodeReroute":
        return [to_socket]
    to_sockets = []
    for link in to_socket.node.outputs[0].links:
        to_sockets.extend(get_terminal_to_sockets(link.to_socket))
    return to_sockets

def transfer_output_value(output, value):
    to_sockets = []
    for link in output.links:
        to_socket = link.to_socket
        to_sockets.extend(get_terminal_to_sockets(to_socket))
    for to_socket in to_sockets:
        to_socket.default_value = value