#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// Node walk state values for marking the status of each node in the pathfinding process
#define UNREACHABLE 0  // Node cannot be reached
#define WALKABLE 10    // Node can be traversed
#define BORDER 20      // Node is on the border of the explored area
#define VISITED 30     // Node has been visited
#define PATH 40        // Node is part of the final path

// precision of diagonal distance
// log10(PRECISION_FACTOR) = how many digits after the comma get preserved
#define PRECISION_FACTOR 10

typedef struct Node Node;
typedef struct Cost Cost;
typedef struct Pos Pos;

// Position structure representing a 2D coordinate
struct Pos {
    int x;
    int y;
};

// Cost structure representing the costs associated with moving to a node
struct Cost {
    int G_cost;  // Movement cost from the start node to the current node
    int H_cost;  // Estimated movement cost from the current node to the end node (heuristic)
    int F_cost;  // Total cost (F = G + H)
};

// Node structure representing a node in the pathfinding graph
struct Node {
    Node *parent;  // Pointer to parent node in the path
    Pos pos;       // Position of the node
    Cost cost;     // Costs associated with the node
    int walkState; // Current state of the node (e.g., UNREACHABLE, WALKABLE)
};

int min(int a, int b) {
    // Returns the smaller of two integers.
    //
    // Inputs:
    //     a (int): The first integer.
    //     b (int): The second integer.
    //
    // Returns:
    //     int: The smaller of the two integers.
    return a < b ? a : b;
}

int max(int a, int b) {
    // Returns the larger of two integers.
    //
    // Inputs:
    //     a (int): The first integer.
    //     b (int): The second integer.
    //
    // Returns:
    //     int: The larger of the two integers.
    return a > b ? a : b;
}

int euclidianDst(Pos *start, Pos *end) {
    // Calculates the Euclidean distance between two positions.
    //
    // Inputs:
    //     start (Pos*): Pointer to the start position.
    //     end (Pos*): Pointer to the end position.
    //
    // Returns:
    //     int: The Euclidean distance between the two positions, scaled by the PRECISION_FACTOR.

    return sqrt(pow(end->x - start->x, 2) + pow(end->y - start->y, 2)) * PRECISION_FACTOR;
}

int offset(int i, int j, Pos *dimensions) {
    // Calculates the offset in a linear array for a 2D coordinate.
    //
    // Inputs:
    //     i (int): The y-coordinate.
    //     j (int): The x-coordinate.
    //     dimensions (Pos*): Pointer to the dimensions of the 2D space.
    //
    // Returns:
    //     int: The offset in the linear array.
    return i * dimensions->x + j;
}

// Function to compare two positions and check if they are the same
int compareNodes(Pos *pos1, Pos *pos2) {
    // Compares two positions to check if they are the same.
    //
    // Inputs:
    //     pos1 (Pos*): Pointer to the first position.
    //     pos2 (Pos*): Pointer to the second position.
    //
    // Returns:
    //     int: 1 if the positions are the same, 0 otherwise.
    return pos1->x == pos2->x && pos1->y == pos2->y;
}
// Function to sort a node into the border array in sorted order based on its F and H costs
void sortInBorderNode(Node *node, Node **border, int *borderNodes) {
    // Sorts a node into the border array in sorted order based on its F and H costs.
    //
    // Inputs:
    //     node (Node*): Pointer to the node to be sorted.
    //     border (Node**): Array of pointers to nodes that are on the border of the explored area.
    //     borderNodes (int*): Pointer to the number of nodes in the border array.
    int pos = *borderNodes - 1;
    int fCost = node->cost.F_cost;
    int hCost = node->cost.H_cost;

    // decrement pos as long as the F Costs are higher and reinsert  
    while(pos > -1 && border[pos]->cost.F_cost > fCost) {
        border[pos + 1] = border[pos];
        pos--;
    }

    // decrement pos as long as the H Costs are higher and reinsert 
    while(pos > -1 && border[pos]->cost.F_cost == fCost && border[pos]->cost.H_cost > hCost) {
        border[pos + 1] = border[pos];
        pos--;
    }

    // insert node at a sorted position
    pos++;
    border[pos] = node;
    (*borderNodes)++;
}

// Function to remove a node from the border array
void removeBorderElement(Node *borderNode, Node **border, int *borderNodes) {
    // Removes a node from the border array.
    //
    // Inputs:
    //     borderNode (Node*): Pointer to the node to be removed.
    //     border (Node**): Array of pointers to nodes in the border.
    //     borderNodes (int*): Pointer to the number of nodes in the border array.
    int found = 0;

    for (int i = 0; i < *borderNodes; i++)
    {
        if(found) {
            border[i - 1] = border[i];
        } else if(compareNodes(&(borderNode->pos), &(border[i]->pos))) {
            found = 1;
        }
    }

    (*borderNodes)--;  
}

// Function to remove the first element of the border array
void shiftBorder(Node **border, int *borderNodes) {
    // Removes the first element of the border array.
    //
    // Inputs:
    //     border (Node**): Array of pointers to nodes in the border.
    //     borderNodes (int*): Pointer to the number of nodes in the border array.
    removeBorderElement(*border, border, borderNodes);
}

int getBorderNodeIdx(Pos *pos, Node **border, int borderNodes) {
    // Retrieves the index of a given node within the border array.
    //
    // Inputs:
    //     pos (Pos*): Pointer to the position of the node.
    //     border (Node**): Array of pointers to nodes in the border.
    //     borderNodes (int): The number of nodes in the border array.
    //
    // Returns:
    //     int: The index of the node in the border array, or -1 if not found.
    Pos borderPos;
    for(int i = 0; i < borderNodes; i++) {
        borderPos = border[i]->pos;
        
        if(compareNodes(pos, &borderPos)) {
            return i;
        }
    }
    return -1;
}

// Function to update the costs and parent of a neighboring node
// returns 1 if the node has changed
int prepareNeighbor(Node *currentBorderNode, Node *parent, Pos *end) {
    // Updates the costs and parent of a neighboring node.
    //
    // Inputs:
    //     currentBorderNode (Node*): Pointer to the current border node.
    //     parent (Node*): Pointer to the parent node.
    //     end (Pos*): Pointer to the end position.
    //
    // Returns:
    //     int: 1 if the node has changed, 0 otherwise.
    int GCostsWithParent = parent->cost.G_cost + euclidianDst(&(currentBorderNode->pos), &(parent->pos));

    if(currentBorderNode->parent == NULL) {
        currentBorderNode->parent = parent;
        currentBorderNode->cost.H_cost = euclidianDst(&(currentBorderNode->pos), end);
        currentBorderNode->cost.G_cost = GCostsWithParent;
        currentBorderNode->cost.F_cost = GCostsWithParent + currentBorderNode->cost.H_cost;
        return 1;
    } else {
        if(GCostsWithParent < currentBorderNode->cost.G_cost) {
            currentBorderNode->parent = parent;
            currentBorderNode->cost.G_cost = GCostsWithParent;
            currentBorderNode->cost.F_cost = GCostsWithParent + currentBorderNode->cost.H_cost;
            return 1;
        }
    }
    return 0;
}

// Function to process all neighboring nodes of the current node in the graph
void computeNeighbors(Node *parent, Pos *end, Node *graph, Node **border, int *borderNodes, Pos *dim) {
    // Processes all neighboring nodes of the current node in the graph.
    //
    // Inputs:
    //     parent (Node*): Pointer to the parent node.
    //     end (Pos*): Pointer to the end position.
    //     graph (Node*): Pointer to the graph of nodes.
    //     border (Node**): Array of pointers to nodes in the border.
    //     borderNodes (int*): Pointer to the number of nodes in the border array.
    //     dim (Pos*): Pointer to the dimensions of the graph.
    Node *currentNode;
    
    for(int i = max(parent->pos.y - 1, 0); i <= min(parent->pos.y + 1, dim->y - 1); i++) {
        for(int j = max(parent->pos.x - 1, 0); j <= min(parent->pos.x + 1, dim->x - 1); j++) {
            // skip parent node
            if(i == parent->pos.y && j == parent->pos.x) continue;
            currentNode = graph + offset(i, j, dim);

            // skip node that was already visited
            if(currentNode->walkState == VISITED) continue;
            // skip node that is an obstacle
            if(!currentNode->walkState) continue;

            int borderIdx = getBorderNodeIdx(&(currentNode->pos), border, *borderNodes);

            if(borderIdx == -1) {
                // add node to border nodes
                prepareNeighbor(currentNode, parent, end);
                sortInBorderNode(currentNode, border, borderNodes);
            } else {
                // check if current node has a smaller distance to its parent
                if(prepareNeighbor(currentNode, parent, end)) {
                    // reinsert changed node
                    removeBorderElement(currentNode, border, borderNodes);
                    sortInBorderNode(currentNode, border, borderNodes);
                }
            }
            currentNode->walkState = BORDER;
        }
    }
}

int astar_algorithm(Pos *start, Pos *end, Node *graph, Node **border, Pos *dim) {
    // Core A* algorithm function to find the shortest path from start to end positions.
    //
    // Inputs:
    //     start (Pos*): Pointer to the start position.
    //     end (Pos*): Pointer to the end position.
    //     graph (Node*): Pointer to the graph of nodes.
    //     border (Node**): Array of pointers to nodes in the border.
    //     dim (Pos*): Pointer to the dimensions of the graph.
    //
    // Returns:
    //     int: The length of the shortest path found, or 0 if no path is found.
    int borderNodes = 0;

    Node *lastNode = graph + offset(start->y, start->x, dim);
    Node *nextNode = graph + offset(start->y, start->x, dim);

    while(!compareNodes(&(nextNode->pos), end)) {
        
        nextNode->walkState = VISITED;
        computeNeighbors(lastNode, end, graph, border, &borderNodes, dim);

        // exit condition if no path found
        if(borderNodes == 0)
            return 0;

        lastNode = nextNode;
        nextNode = border[0];
        shiftBorder(border, &borderNodes);
    }

    // nextNode is the goal node and all G values which represent the distance are cumulated in its G Costs
    int pathLength = nextNode->cost.G_cost;

    while(1) {
        nextNode->walkState = PATH;

        // terminate loop if start node was reached
        if(nextNode->parent == NULL) {
            break;
        }
        nextNode = nextNode->parent;
    }
    
    return pathLength;
}

// Function to run the A* algorithm and return the distance of the found path
float run_astar(Pos *start, Pos *end, Node *graph, Pos *dims) {
    // Executes the A* algorithm and returns the distance of the found path.
    //
    // Inputs:
    //     start (Pos*): Pointer to the start position.
    //     end (Pos*): Pointer to the end position.
    //     graph (Node*): Pointer to the graph of nodes.
    //     dims (Pos*): Pointer to the dimensions of the graph.
    //
    // Returns:
    //     float: The distance of the found path, or -1 if memory allocation failed.

    // allocate memory for a pointer array that point to a node that is on the border of all visited nodes
    // size is the perimeter of the maze defined in the csv file
    // this should be more than enough for the calculations
    Node **border = malloc(2 * (dims->x + dims->y) * sizeof(Node*));

    // check if memory could be allocated
    if(border == NULL) {
        return -1;
    }

    int pathLength = astar_algorithm(start, end, graph, border, dims);
    // since each G Cost was calculated as ints with a factor of PRECISION_FACTOR it needs to be accounted for
    float distance = pathLength / (float) PRECISION_FACTOR;

    free(border);
    
    return distance;
}