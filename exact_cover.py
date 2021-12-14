from dimod import BinaryQuadraticModel

def exact_cover_bqm(problem_set, subsets):  
    
    bqm = BinaryQuadraticModel({}, {}, 0, 'BINARY') #no bias and zero offset

    for element in problem_set: 
        bqm.offset += 1

        for i in range(len(subsets)):
            if element in subsets[i]:
                bqm.add_variable(i, -1) #add variable and its bias to bqm

                for j in range(i):         
                    if element in subsets[j]:
                        bqm.add_interaction(i, j, 2) #add an interaction + quadratic bias to bqm

    return bqm
