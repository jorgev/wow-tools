// raid_detail.js

goog.require('goog.ui.tree.TreeControl');

var tree;

function createTreeFromCombatData(node, data) {
	node.setHtml(data[0]);
	if (data.length > 1) {
		var children = data[1];
		var childNotCollapsible = 3; // Hard coded to reduce randomness.
		for (var i = 0; i < children.length; i++) {
			var child = children[i];
			var childNode = node.getTree().createNode();

			node.add(childNode);
			createTreeFromTestData(childNode, child);

			if (i == childNotCollapsible && child.length > 1) {
				childNode.setIsUserCollapsible(false);
				childNode.setExpanded(true);
				nonCollapseNode = childNode;
			}
		}
	}
}
