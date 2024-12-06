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

    apply_and_rule_1(sampleWorld, element0)
    #print(f"Num Concepts before: {len(element0.concepts)}")
    apply_and_rule_2(element0)
    #print(f"Num Concepts after: {len(element0.concepts)}")
    apply_exist_rule_1(element0)


def apply_t_rule(world, element):
    pass

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

def apply_exist_rule_1(element: Element):
    concepts = element.concepts

    for concept in concepts:
        conceptType = concept.getClass().getSimpleName()
        if conceptType == "ExistentialRoleRestriction":
            role = concept.role()
            if not element.connections[role]
            print("I found an existential role restriction: "+formatter.format(concept))
            print("The role is: "+formatter.format(concept.role()))
            print("The filler is: "+formatter.format(concept.filler()))
            

def apply_exist_rule_2():
    pass

def apply_sub_rule():
    pass

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
