class Element:
    def __init__(self, name):
        """
        Initialize an Element with a name and its associated concepts.
        
        :param name: Unique identifier for the element
        """
        self.name = name
        self.concepts = []  # Changed from set to list
        self.connections = {}  # Stores named, directed connections to other elements
    
    def add_concept(self, *concepts):
        """
        Add one or more concepts to the element's list of concepts.
        
        :param concepts: One or more concepts or a list of concepts to be added
        """
        # Flatten the input in case a list is passed
        flat_concepts = []
        for concept in concepts:
            if isinstance(concept, list):
                flat_concepts.extend(concept)
            else:
                flat_concepts.append(concept)
        
        # Add concepts while preventing duplicates
        for concept in flat_concepts:
            if concept not in self.concepts:
                self.concepts.append(concept)
    
    def remove_concept(self, concept):
        """
        Remove a concept from the element's list of concepts.
        
        :param concept: Concept to be removed
        """
        if concept in self.concepts:
            self.concepts.remove(concept)
    
    def connect_to(self, other_element, relation_name):
        """
        Create a directed connection to another element with a specific relation name.
        
        :param other_element: Element to connect to
        :param relation_name: Name of the relation
        """
        if relation_name not in self.connections:
            self.connections[relation_name] = set()
        self.connections[relation_name].add(other_element)
    
    def get_connections(self, relation_name=None):
        """
        Retrieve connections, optionally filtered by relation name.
        
        :param relation_name: Optional specific relation to filter by
        :return: Set of connected elements
        """
        if relation_name:
            return self.connections.get(relation_name, set())
        return set(elem for connection_set in self.connections.values() for elem in connection_set)
    
    def __repr__(self):
        """
        String representation of the Element.
        
        :return: Detailed string describing the element
        """
        return (f"Element(name={self.name}, "
                f"concepts={self.concepts}, "
                f"connections={self.connections})")


class World:
    def __init__(self):
        """
        Initialize a World with an empty list of elements.
        """
        self.elements = []
    
    def add_element(self, element):
        """
        Add an element to the world.
        
        :param element: Element to be added
        """
        # Prevent duplicate elements
        if element not in self.elements:
            self.elements.append(element)
    
    def remove_element(self, element):
        """
        Remove an element from the world.
        
        :param element: Element to be removed
        """
        if element in self.elements:
            self.elements.remove(element)
    
    def get_element_by_name(self, name):
        """
        Find an element by its name.
        
        :param name: Name of the element to find
        :return: Element with the given name, or None if not found
        """
        for element in self.elements:
            if element.name == name:
                return element
        return None
    
    def __repr__(self):
        """
        String representation of the World.
        
        :return: Detailed string describing the world's elements
        """
        return f"World(elements={self.elements})"