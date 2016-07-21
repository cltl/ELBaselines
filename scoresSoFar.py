import utils

print("########################### MY SYSTEM ######################")
p, r, f=utils.computeStats("aidaMyOutput.tsv", False)
print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))

print("########################### AGDISTIS ######################")
p, r, f=utils.computeStats("aidaMyOutput.tsv", True)
print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))
