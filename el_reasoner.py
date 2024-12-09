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
    # subsumerStr = formatter.format(random.choice(conceptNames))
    conceptNames = ontology.getConceptNames()
    subsumee = elFactory.getConceptName(class_name)
    subsumer = elFactory.getConceptName("Protein")
    # transform each equivalence axioms to two subsumptions
    remove_alc_axioms()
    remove_equivalence_axioms()

    world = World()
    init_element = Element(0)
    init_element.add_concept(subsumee)
    world.add_element(init_element)

    changed = True
    while changed:
        changed = False
        for el in world.elements:
            sub_changed = apply_sub_rule(el)
            and1_changed = apply_and_rule_1(el)
            exist1_changed = apply_exist_rule_1(world, el)
            and2_changed = apply_and_rule_2(el)
            exist2_changed = apply_exist_rule_2(el)
            t_changed = apply_t_rule(el)

            changed = changed or sub_changed or and1_changed or exist1_changed or \
                    and2_changed or exist2_changed or t_changed
        
    for subsumer in conceptNames:
        if subsumer in init_element.concepts:
            print(f"{formatter.format(subsumer)}")
            # Satisifed

    
    # TO-DO: -> Check that only concepts from the input are assigned 

    # sampleWorld = World()
    # element0 = Element(0)
    # element0.add_concept(random.sample(allConcepts, 10))
    # sampleWorld.add_element(element0)

    # apply_t_rule(sampleWorld, element0)
    # apply_and_rule_1(sampleWorld, element0)
    # #print(f"Num Concepts before: {len(element0.concepts)}")
    # apply_and_rule_2(element0)
    # #print(f"Num Concepts after: {len(element0.concepts)}")
    # apply_exist_rule_1(sampleWorld, element0)
    # print(f"\nWorld after:\n{sampleWorld}\n")
    # print("-----")
    # apply_exist_rule_2(sampleWorld, element0)
    # print("-----")
    # apply_sub_rule(sampleWorld, element0)

def remove_alc_axioms():
   global allConcepts, axioms
   allowedConceptTypes = ["ConceptName", "TopConcept$", "ExistentialRoleRestriction", "ConceptConjunction"]

   # Filter concepts
   allConcepts = [concept for concept in allConcepts if concept.getClass().getSimpleName() in allowedConceptTypes]

   # Filter axioms containing disallowed concepts
   filtered_axioms = []
   for axiom in axioms:
       keep_axiom = True
       
       # Check concepts in GCI axioms
       if axiom.getClass().getSimpleName() == "GeneralConceptInclusion":
           lhs_type = axiom.lhs().getClass().getSimpleName()
           rhs_type = axiom.rhs().getClass().getSimpleName()
           if lhs_type not in allowedConceptTypes or rhs_type not in allowedConceptTypes:
               keep_axiom = False
               
       # Check concepts in equivalence axioms        
       elif axiom.getClass().getSimpleName() == "EquivalenceAxiom":
           for concept in axiom.getConcepts():
               if concept.getClass().getSimpleName() not in allowedConceptTypes:
                   keep_axiom = False
                   break
                   
       if keep_axiom:
           filtered_axioms.append(axiom)
           
   axioms = filtered_axioms

def apply_t_rule(element: Element):
    """
    Apply T-rule for an element by adding the top concept
    
    :param world: The world containing all elements
    :param element: The element to apply the rule to
    """
    alteredInterpretation = False
    # Create the top concept using elFactory
    top_concept = elFactory.getTop()
    
    if top_concept not in element.concepts:
        # print(f"Adding top concept: {formatter.format(top_concept)}")
        element.add_concept(top_concept)
        alteredInterpretation = True

    return alteredInterpretation 

def apply_and_rule_1(element: Element):
    alteredInterpretation = False
    concepts = element.concepts

    for concept in concepts:
        conceptType = concept.getClass().getSimpleName()
        if conceptType == "ConceptConjunction":
            # print(formatter.format(concept))
            conjuncts = concept.getConjuncts()
            if len(conjuncts) != 2:
                print("And-Rule-1 Conjunction Error")
                continue

            newConceptA = conjuncts[0]
            newConceptB = conjuncts[1]

            element.concepts.append(newConceptA)
            element.concepts.append(newConceptB)
            alteredInterpretation = True

    return alteredInterpretation

def apply_and_rule_2(element: Element):
    alteredInterpretation = False
    concepts = element.concepts
    
    # Generate all unique combinations of 2 concepts
    # itertools.combinations ensures no repeated pairs and no (a,a) combinations
    for a, b in itertools.combinations(concepts, 2):
        conjunction = elFactory.getConjunction(a, b)
        
        # Check if conjunction is in allConcepts
        if conjunction in allConcepts:
            # print(f"Adding conjunction: {formatter.format(conjunction)}")
            element.add_concept(conjunction)
            alteredInterpretation = True

    return alteredInterpretation

def apply_exist_rule_1(world: World, element: Element):
    """
    Apply existential rule 1 for an element
    
    :param world: The world containing all elements
    :param element: The element to apply the rule to
    """
    #print(f"World before:\n{world}\n")
    alteredInterpretation = False
    concepts = element.concepts

    for concept in concepts:
        conceptType = concept.getClass().getSimpleName()
        
        # Check if the concept is an existential role restriction
        if conceptType == "ExistentialRoleRestriction":
            role = concept.role()
            filler = concept.filler()
            
            # Print debug information
            # print("Found existential role restriction: " + formatter.format(concept))
            # print("Role: " + formatter.format(role))
            # print("Filler: " + formatter.format(filler))
            
            # Check if this role already has successors
            role_str = formatter.format(role)
            if role_str not in element.connections:
                element.connections[role_str] = set()
            
            # Check existing successors for the role
            for successor in element.connections.get(role_str, set()):
                # Check if the filler concept is in any of the successor's concepts
                if successor.concepts and filler in successor.concepts:
                    # print("Concept already satisifed!")
                    return alteredInterpretation
            
            # Try to find an existing element with the filler as initial concept
            matching_element = None
            for e in world.elements:
                if e.concepts and formatter.format(e.concepts[0]) == formatter.format(filler):
                    matching_element = e
                    break
            
            if matching_element:
                # print("Found a matching element with correct init concept")
                # Use existing element as successor
                element.connect_to(matching_element, role_str)
            else:
                # print("Creating new element")
                # Create a new element with the filler as initial concept
                new_element = Element(len(world.elements))
                new_element.add_concept(filler)
                
                # Add the new element to the world
                world.add_element(new_element)
                
                # Connect the new element as a successor
                element.connect_to(new_element, role_str)
            
            return True

def apply_exist_rule_2(element: Element):
    """
    Apply existential rule 2 for an element
    
    :param world: The world containing all elements
    :param element: The element to apply the rule to
    """
    alteredInterpretation = False
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
                        #print(f"Adding existential concept: {formatter.format(existential_concept)}")
                        element.add_concept(existential_concept)
                        alteredInterpretation = True
                    
    return alteredInterpretation

def apply_sub_rule(element: Element):
    """
    Apply subsumption rule for an element
    
    :param world: The world containing all elements
    :param element: The element to apply the rule to
    """
    alteredInterpretation = False
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
                            # print(f"Adding subsumer: {formatter.format(subsumer)} "
                            #       f"for concept: {formatter.format(concept)}")
                            element.add_concept(subsumer)
                            alteredInterpretation = True
    
    return alteredInterpretation

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
    
    #print(f"Number of axioms after transformation: {len(axioms)}")

def process_ontology(ontology_file, class_name):
    """
    Process the ontology file and perform actions related to the class name.
    """
    global conceptNames

    #print(f"Processing ontology file '{ontology_file}' for class '{class_name}'.")
    
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

    #print(f"Loading ontology from file: {ontology_file}...")

    try:
        ontology = parser.parseFile(ontology_file)

        gateway.convertToBinaryConjunctions(ontology)

        # Extract TBox axioms and concepts
        tbox = ontology.tbox()
        axioms = list(tbox.getAxioms())
        allConcepts = list(ontology.getSubConcepts())
        conceptNames = list(ontology.getConceptNames())

        # print_ontology_summary()

    except Exception as e:
        print(f"Error loading ontology: {e}")

def print_ontology_summary():
    """
    Print a summary of the loaded ontology.
    """
    print(f"There are {len(axioms) if axioms else 0} axioms in the TBox.")
    for axiom in axioms:
        print(formatter.format(axiom))
    print(f"There are {len(allConcepts) if allConcepts else 0} concepts in the ontology.")
    print([formatter.format(x) for x in allConcepts])
    print(f"There are {len(conceptNames) if conceptNames else 0} concept names in the ontology.")

if __name__ == "__main__":
    main()
