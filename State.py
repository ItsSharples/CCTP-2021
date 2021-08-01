####################################################
from typing import Any, Dict, List, Tuple, Union



StateContents = List[Tuple[str, str]]
StateType = Dict[str, StateContents]
Operator = Dict[str, Union[StateType, List]]
EventType = Dict[str, Union[StateType, List]]

StartingState : StateType
Operators : Dict[str, Operator]
Events: Dict[str, EventType]
OriginalGoal : StateType

StartingState = {
	"at" : [("Actor", "Home"), ("Scarecrow", "Field"), ("Tools", "Shed"), ("Seeds", "Shed")],
	"graspable" : ["Tools", "Seeds"],
	"farmable" : ["Trees", "Crops"],
	"cookable" : ["Crops"],
	"consumable" : ["Food"]
}

Operators = {
	"Go" : {
	"Arguments" : ["x", "y"],
	"Requires": {
		"at" : [("Actor", "x")]
	},
	"Effect" : {
		"at" : [("Actor", "y"), ("Actor", "x", "Not")]
	},
	"Format" : "from {} to {}"
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
		"at" : [("crop", "x"), ("Tools", "Inventory"), ("Actor", "x")],
		"farmable" : ["crop"]
	},
	"Effect" : {
		"at" : [("crop", "x", "Not"), ("crop", "Inventory"), ("Seeds", "Field")],
		"hungry" : [("Actor", "is")]
	}},

	"Plant" : {
	"Arguments" : ["sapling"],
	"Requires" : {
		"at" : [("Actor", "Forest"), ("sapling", "Inventory")]
	},
	"Effect" : {
		"at" : [("Tree", "Forest"), ("sapling", "Inventory", "Not")]
	}},
	"Chop" : {
	"Arguments" : ["tree"],
	"Requires" : {
		"at" : [("tree", "x"), ("Tools", "Inventory"), ("Actor", "Forest")],
		"farmable" : ["tree"]
	},
	"Effect" : {
		"at" : [("tree", "x", "Not"), ("Logs", "Forest")],
		"hungry" : [("Actor", "is")]
	}},
# Food Eating
	"Cook" : {
	"Arguments" : ["crop"],
	"Requires" : {
		"at" : [("crop", "Inventory"), ("Actor", "Home")],
		"cookable" : ["crop"]
	},
	"Effect" : {
		"at" : [("crop", "Inventory", "Not"), ("Food", "Home")]
	}},
	# "Eat" : {
	# "Arguments" : ["food"],
	# "Requires" : {
	# 	"at" : [("food", "Inventory")],
	# 	"consumable" : ["food"]
	# },
	# "Effect" : {
	# 	"at" : [("food", "Inventory", "Not")],
	# 	"hungry" : [("Actor", "is", "Not")]
	# }},
}

OriginalGoal = {
	"at" : [("Actor", "Field"), ("Crops", "Home"), ("Tools", "Shed")],
}
####################################################

Events = {
	"Move" : {
		"Arguments" : ["thing", "x", "y"],
		"Infers" : ["x"],
		"Effect" : {
			"at" : [("thing", "x", "Not"), ("thing", "y")]
		},
		"Format" : "{} from {} to {}"
	},
	"Scarecrow Theft" :
	{
		"Arguments" : [],
		"Infers" : ["x"],
		"Effect" : {
			"at" : [("Scarecrow", "x", "Not"), ("Scarecrow", "Far Away")]
		}
	}
}
####################################################


# Things that aren't arguments, but can be used to make Operations more generic
# x is where the Actor is currently, y are Locations the Actor can go to, c is climb, h is height
Known_Fudges = ["x", "y", "c", "h"]
Special_Locations = ["Inventory", "Far Away"]

#########

def SortState(input: StateType) -> StateType:
	## Sort State to enable good hash
	for type in input:
		input[type] = sorted(input[type])
	return input

def IsSpecialLocation(location: str) -> bool:
    return location in Special_Locations
