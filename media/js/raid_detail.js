// raid_detail.js

goog.require('goog.dom');
goog.require('goog.ui.tree.TreeControl');

function createTreeFromCombatData(node, data) {
	node.setHtml(data[0]);
	if (data.length > 1) {
		var children = data[1];
		for (var i = 0; i < children.length; i++) {
			var child = children[i];
			var childNode = node.getTree().createNode();

			node.add(childNode);
			createTreeFromCombatData(childNode, child);
		}
	}
}
