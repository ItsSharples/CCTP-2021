####################################################
StateType = "dict[str, Any]"

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
####################################################


# Things that aren't arguments, but can be used to make Operations more generic
Known_Fudges = ["x", "y", "c", "h"]


#########

def SortState(input: StateType) -> StateType:
	## Sort State to enable good hash
	for type in input:
		input[type] = sorted(input[type])
	return input