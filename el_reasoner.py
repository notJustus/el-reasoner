import sys
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
        axioms = tbox.getAxioms()
        allConcepts = ontology.getSubConcepts()
        conceptNames = ontology.getConceptNames()

        print_ontology_summary()

    except Exception as e:
        print(f"Error loading ontology: {e}")

def print_ontology_summary():
    """
    Print a summary of the loaded ontology.
    """
    print(f"There are {len(axioms) if axioms else 0} axioms in the TBox.")
    print(f"There are {len(allConcepts) if allConcepts else 0} concepts in the ontology.")
    print(f"There are {len(conceptNames) if conceptNames else 0} concept names in the ontology.")

if __name__ == "__main__":
    main()
