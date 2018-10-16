from graphviz import Digraph


class ActionsPlotter:
    """ActionsPlotter plots actions chain to image as a graph.

    Used graphviz backend.
    """
    def __init__(self):
        self.graph = None
        self.sub_graph = None
        self.node_num = 0
        self.cluster_num = 0

    def plot(self, action, filename, format='pdf'):
        """
        render `action` chain into image file

        Parameters
        ----------
        action : Action - root action of the workflow
        filename : string - file name of the image
        format : string - image format
        """
        self.graph = Digraph(format=format)
        self.sub_graph = self.graph
        self._plot_dispatch(action)
        self.graph.render(filename)

    def _plot_dispatch(self, action, prev_node=None, edge_label=None):
        type_name = type(action).__name__
        custom_func = custom_plot_functions.get(type_name, None)
        if custom_func is not None:
            custom_func(self, action, prev_node, edge_label)
        else:
            self._plot_Action(action, prev_node, edge_label)

    def _plot_Action(self, action, prev_node, edge_label):
        current_node = self.node_num
        self.sub_graph.node(str(current_node), action.__class__.__name__)
        self.node_num += 1
        if prev_node is not None:
            self.sub_graph.edge(str(prev_node), str(current_node), constraint='false', label=edge_label)
        self._plot_next_and_for_each_actions(action, current_node)

    def _plot_next_and_for_each_actions(self, action, prev_node):
        if action.for_each_action is not None:
            self._plot_dispatch(action.for_each_action, prev_node, edge_label='for_each')
        if action.next_action is not None:
            self._plot_dispatch(action.next_action, prev_node)


# Below are custom plot functins for particular Actions
def _plot_FieldsTransform(self, action, prev_node, edge_label):
    current_node = self.node_num
    self.sub_graph.node(str(current_node), action.__class__.__name__)
    self.node_num += 1
    if prev_node is not None:
        self.sub_graph.edge(str(prev_node), str(current_node), constraint='false', label=edge_label)

    if action.transformations:
        with self.sub_graph.subgraph(name=str(self.cluster_num)) as c:
            self.cluster_num += 1
            c.attr(label=action.__class__.__name__)
            c.node_attr.update(style='filled')
            c.attr(color='blue')
            prev_sub_graph = self.sub_graph
            self.sub_graph = c
            for name, subaction in action.transformations.items():
                self._plot_dispatch(subaction, current_node, edge_label="'{}'".format(name))
            self.sub_graph = prev_sub_graph

    self._plot_next_and_for_each_actions(action, current_node)


def _plot_GetField(self, action, prev_node, edge_label):
    current_node = self.node_num
    self.sub_graph.node(str(current_node), "{}\n'{}'".format(action.__class__.__name__, action.field))
    self.node_num += 1
    if prev_node is not None:
        self.sub_graph.edge(str(prev_node), str(current_node), constraint='false', label=edge_label)

    self._plot_next_and_for_each_actions(action, current_node)


def _plot_ModelObjectCreate(self, action, prev_node, edge_label):
    fields_desc = []
    for field in action.fields:
        orm_field = action.fields_map.get(field)
        if orm_field:
            fields_desc.append("{} (from '{}')".format(orm_field, field))
        else:
            fields_desc.append("{}".format(field))

    label = '{}\n\n{}({})'.format(action.__class__.__name__,
                                  action.orm_model.__name__,
                                  ',\n'.join(fields_desc)
                                  )

    current_node = self.node_num
    self.sub_graph.node(str(current_node), label)
    self.node_num += 1
    if prev_node is not None:
        self.sub_graph.edge(str(prev_node), str(current_node), constraint='false', label=edge_label)

    self._plot_next_and_for_each_actions(action, current_node)


# expandable list of custom plot functions for Action
custom_plot_functions = {
    'FieldsTransform': _plot_FieldsTransform,
    'GetField': _plot_GetField,
    'ModelObjectCreate': _plot_ModelObjectCreate,
}
