import sys
import random
import itertools
from World import World, Element
from py4j.java_gateway import JavaGateway  # type: ignore

# Initialize the Java Gateway connection
gateway = JavaGateway()

# Get necessary components from the gateway
parser = gateway.getOWLParser()
formatter = gateway.getSimpleDLFormatter()
elFactory = gateway.getELFactory()

random.seed(60)

# Global variables
ontology = None
tbox = None
axioms = None
allConcepts = None
conceptNames = None

def main():
    # Validate the input
    if len(sys.argv) != 3:
        print("Usage: PROGRAM_NAME ONTOLOGY_FILE CLASS_NAME")
        sys.exit(1)

    # Parse the arguments
    ontology_file = sys.argv[1]
    class_name = sys.argv[2]

    process_ontology(ontology_file, class_name)

    apply_el_alorithm(class_name)

def apply_el_alorithm(class_name):
    # Start with one subsumer. Later just do a for loop that iterates over all conceptNames
    subsumerStr = random.choice(conceptNames)
    #subsumer = elFactory.getConceptName(subsumerStr)
    #subsumee = elFactory.getConceptName(class_name)
    world = World()
    # transform each equivalence axioms to two subsumptions
    remove_equivalence_axioms()

    sampleWorld = World()
    element0 = Element(0)
    element0.add_concept(random.sample(allConcepts, 10))
    sampleWorld.add_element(element0)

    apply_and_rule_1(sampleWorld, element0)
    #print(f"Num Concepts before: {len(element0.concepts)}")
    apply_and_rule_2(element0)
    #print(f"Num Concepts after: {len(element0.concepts)}")
    apply_exist_rule_1(sampleWorld, element0)
    print(f"\nWorld after:\n{sampleWorld}\n")
    print("-----")
    apply_exist_rule_2(sampleWorld, element0)
    print("-----")
    apply_sub_rule(sampleWorld, element0)


def apply_t_rule(world: World, element: Element):
    """
    Apply T-rule for an element by adding the top concept
    
    :param world: The world containing all elements
    :param element: The element to apply the rule to
    """
    # Create the top concept using elFactory
    top_concept = elFactory.getTop()
    
    # Check if the top concept is in allConcepts
    if top_concept in allConcepts:
        # Add the top concept to the element if not already present
        if top_concept not in element.concepts:
            print(f"Adding top concept: {formatter.format(top_concept)}")
            element.add_concept(top_concept)

def apply_and_rule_1(world, element: Element):
    concepts = element.concepts

    for concept in concepts:
        conceptType = concept.getClass().getSimpleName()
        if conceptType == "ConceptConjunction":
            print(formatter.format(concept))
            conjuncts = concept.getConjuncts()
            if len(conjuncts) != 2:
                print("And-Rule-1 Conjunction Error")
                continue

            newConceptA = conjuncts[0]
            newConceptB = conjuncts[1]

            element.concepts.append(newConceptA)
            element.concepts.append(newConceptB)

def apply_and_rule_2(element: Element):
    concepts = element.concepts
    
    # Generate all unique combinations of 2 concepts
    # itertools.combinations ensures no repeated pairs and no (a,a) combinations
    for a, b in itertools.combinations(concepts, 2):
        conjunction = elFactory.getConjunction(a, b)
        
        # Check if conjunction is in allConcepts
        if conjunction in allConcepts:
            print(f"Adding conjunction: {formatter.format(conjunction)}")
            element.add_concept(conjunction)

def apply_exist_rule_1(world: World, element: Element):
    """
    Apply existential rule 1 for an element
    
    :param world: The world containing all elements
    :param element: The element to apply the rule to
    """
    print(f"World before:\n{world}\n")
    concepts = element.concepts

    for concept in concepts:
        conceptType = concept.getClass().getSimpleName()
        
        # Check if the concept is an existential role restriction
        if conceptType == "ExistentialRoleRestriction":
            role = concept.role()
            filler = concept.filler()
            
            # Print debug information
            print("Found existential role restriction: " + formatter.format(concept))
            print("Role: " + formatter.format(role))
            print("Filler: " + formatter.format(filler))
            
            # Check if this role already has successors
            role_str = formatter.format(role)
            if role_str not in element.connections:
                element.connections[role_str] = set()
            
            # Flag to track if the restriction is already satisfied
            restriction_satisfied = False
            
            # Check existing successors for the role
            for successor in element.connections.get(role_str, set()):
                # Check if the filler concept is in any of the successor's concepts
                if successor.concepts and filler in successor.concepts:
                    print("Concept already satisifed!")
                    restriction_satisfied = True
                    break
            
            # If restriction is not satisfied
            if not restriction_satisfied:
                # Try to find an existing element with the filler as initial concept
                matching_element = None
                for e in world.elements:
                    if e.concepts and formatter.format(e.concepts[0]) == formatter.format(filler):
                        matching_element = e
                        break
                
                if matching_element:
                    print("Found a matching element with correct init concept")
                    # Use existing element as successor
                    element.connect_to(matching_element, role_str)
                else:
                    print("Creating new element")
                    # Create a new element with the filler as initial concept
                    new_element = Element(len(world.elements))
                    new_element.add_concept(filler)
                    
                    # Add the new element to the world
                    world.add_element(new_element)
                    
                    # Connect the new element as a successor
                    element.connect_to(new_element, role_str)

def apply_exist_rule_2(world: World, element: Element):
    """
    Apply existential rule 2 for an element
    
    :param world: The world containing all elements
    :param element: The element to apply the rule to
    """
    # Iterate through all roles (connection types) for this element
    for role_str, successors in element.connections.items():
        # Check each successor
        for successor in successors:
            # Iterate through all concepts of the successor
            for concept in successor.concepts:
                # Create an existential role restriction
                existential_concept = elFactory.getExistentialRoleRestriction(
                    elFactory.getRole(role_str), 
                    concept
                )
                
                # Check if the existential concept is in allConcepts
                if existential_concept in allConcepts:
                    # Add the concept to the element if it's not already present
                    if existential_concept not in element.concepts:
                        print(f"Adding existential concept: {formatter.format(existential_concept)}")
                        element.add_concept(existential_concept)

def apply_sub_rule(world: World, element: Element):
    """
    Apply subsumption rule for an element
    
    :param world: The world containing all elements
    :param element: The element to apply the rule to
    """
    # Create a copy of the current concepts to iterate over
    current_concepts = element.concepts.copy()
    
    for concept in current_concepts:
        # Iterate through all axioms in the tbox
        for axiom in axioms:
            # Check if the axiom is a General Concept Inclusion (GCI) axiom
            axiom_type = axiom.getClass().getSimpleName()
            if axiom_type == "GeneralConceptInclusion":
                # Get the subsumee and subsumer of the axiom
                subsumee = axiom.lhs()
                subsumer = axiom.rhs()
                #print(f"Concept: {formatter.format(concept)}, Subsumee: {formatter.format(subsumee)}")
                
                # Check if the current concept matches the subsumee
                if concept == subsumee:
                    # Check if the subsumer is in allConcepts to ensure validity
                    if subsumer in allConcepts:
                        # Add the subsumer to the element if not already present
                        if subsumer not in element.concepts:
                            print(f"Adding subsumer: {formatter.format(subsumer)} "
                                  f"for concept: {formatter.format(concept)}")
                            element.add_concept(subsumer)

def remove_equivalence_axioms():
    global axioms
    newAxioms = []
    
    axioms_copy = axioms.copy()
    
    for axiom in axioms_copy:
        axiomType = axiom.getClass().getSimpleName()
        
        if axiomType == "EquivalenceAxiom":
            subConcepts = axiom.getConcepts()
            
            if len(subConcepts) != 2:
                print(f"Equivalence axiom error: Axiom does not consist of two sub-concepts")
                continue
            
            # Create two new axioms representing the bidirectional subsumption
            newAxiomA = elFactory.getGCI(subConcepts[0], subConcepts[1])
            newAxiomB = elFactory.getGCI(subConcepts[1], subConcepts[0])
            
            # Append the new axioms to the newAxioms list
            newAxioms.append(newAxiomA)
            newAxioms.append(newAxiomB)
            
            # Remove the original equivalence axiom from the axioms list
            axioms.remove(axiom)
    
    axioms.extend(newAxioms)
    
    print(f"Number of axioms after transformation: {len(axioms)}")

def process_ontology(ontology_file, class_name):
    """
    Process the ontology file and perform actions related to the class name.
    """
    global conceptNames

    print(f"Processing ontology file '{ontology_file}' for class '{class_name}'.")
    
    # Load the ontology
    load_ontology(ontology_file)

    # Validate if the class name exists in the ontology
    if conceptNames is None or elFactory.getConceptName(class_name) not in conceptNames:
        print(f"--Input Error: {class_name} does not exist in ontology: {ontology_file}")
        return

def load_ontology(ontology_file):
    """
    Load an ontology from a file and convert it to binary conjunctions.
    """
    global ontology, tbox, axioms, allConcepts, conceptNames

    print(f"Loading ontology from file: {ontology_file}...")

    try:
        ontology = parser.parseFile(ontology_file)

        gateway.convertToBinaryConjunctions(ontology)

        # Extract TBox axioms and concepts
        tbox = ontology.tbox()
        axioms = list(tbox.getAxioms())
        allConcepts = list(ontology.getSubConcepts())
        conceptNames = list(ontology.getConceptNames())

        print_ontology_summary()

    except Exception as e:
        print(f"Error loading ontology: {e}")

def print_ontology_summary():
    """
    Print a summary of the loaded ontology.
    """
    print(f"There are {len(axioms) if axioms else 0} axioms in the TBox.")
    # for axiom in axioms:
    #     print(formatter.format(axiom))
    print(f"There are {len(allConcepts) if allConcepts else 0} concepts in the ontology.")
    # print([formatter.format(x) for x in allConcepts])
    print(f"There are {len(conceptNames) if conceptNames else 0} concept names in the ontology.")

if __name__ == "__main__":
    main()
