# =========================================================================
# reload the graph items
# =========================================================================
import mix.mix_object as mix_object
reload(mix_object)

import mix.mix_dict as mix_dict
reload(mix_dict)

import mix.mix_attribute as mix_attribute
reload(mix_attribute)

import mix.mix_node as mix_node
reload(mix_node)

import mix.mix_graph as mix_graph
reload(mix_graph)


# =========================================================================
# reload the models
# =========================================================================
import mix.ui.graph_model
reload(mix.ui.graph_model)

import mix.ui.abstract_graph_model as abstract_graph_model
reload(abstract_graph_model)

import mix.ui.psd_model as psd_model
reload(psd_model)

import mix.ui.psd_model_maya as psd_model_maya
reload(psd_model_maya)

import mix.ui.weights_model as weights_model
reload(weights_model)

import mix.ui.weights_model_maya as weights_model_maya
reload(weights_model_maya)

import mix.ui.model_manager as model_manager
reload(model_manager)

# =========================================================================
# reload view items
# =========================================================================
import mix.ui.input_dialog
reload(mix.ui.input_dialog)

import mix.ui.radial_menu as radial_menu
reload(radial_menu)

import mix.ui.graph_tree_item as graph_tree_item
reload(graph_tree_item)

import mix.ui.graph_tree_view
reload(mix.ui.graph_tree_view)

import mix.ui.graph_widget
reload(mix.ui.graph_widget)

import mix.ui.main_window as main_window
main_window.MainWindow.delete_callbacks()
reload(main_window)

def launch():
    main_window.launch()

if __name__ == '__main__':
    launch()