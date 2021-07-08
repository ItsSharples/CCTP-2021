####################################################
StateType = 'dict[str, dict]'

StartingState : StateType = {
	"at" : [("Actor", "Home"), ("Scarecrow", "Field"), ("Tools", "Shed"), ("Seeds", "Shed")],
	"graspable" : ["Tools", "Seeds"],
	"farmable" : ["Crops"]
}

Operators : StateType = {
	"Go" : {
	"Arguments" : ["x", "y"],
	"Requires": {
		"at" : [("Actor", "x")]
	},
	"Effect" : {
		"at" : [("Actor", "y"), ("Actor", "x", "Not")]
	}
	},
# General Interaction
	"Grasp" : {
	"Arguments" : ["grab"],
	"Requires":{
		"at" : [("Actor","x"), ("grab","x")],
		"graspable" : ["grab"]
	},
	"Effect" : {
		"have" : [("Actor", "grab")],
		"at":[("grab", "Inventory"), ("grab", "x", "Not")]
	}
	},
	"Drop" : {
	"Arguments" : ["drop"],
	"Requires":{
        "at" : [("Actor", "x"), ("drop", "Inventory")]
        },
	"Effect" : {
		"at" : [("drop", "x"), ("drop", "Inventory", "Not")]
	}
	},
# Farming Stuff
	"Grow" : {
	"Arguments" : ["seed"],
	"Requires" : {
		"at" : [("Actor", "Field"), ("seed", "Inventory")]
	},
	"Effect" : {
		"at" : [("Crops", "Field"), ("seed", "Inventory", "Not")]
	}
	},

	"Farm" : {
	"Arguments" : ["crop"],
	"Requires" : {
		"at" : [("crop", "x"), ("Tools", "Inventory"), ("Actor", "Field")],
		"farmable" : ["crop"]
	},
	"Effect" : {
		"at" : [("crop", "x", "Not"), ("crop", "Inventory")]
	}
	}
}

OriginalGoal : StateType = {
	"at" : [("Actor", "Field"), ("Crops", "Home"), ("Tools", "Shed")],
}
