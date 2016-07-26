import utils

#fn="aidaArticles.tsv"
#fn="aidaTopLevel.tsv"
fn="extraFullLowLevel.tsv"
#fn="aidaLowLevel.tsv"
#print("########################### MY SYSTEM ######################")
#p, r, f=utils.computeStats(fn, False)
#print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))

print("########################### AGDISTIS ######################")
p, r, f=utils.computeStats(fn, True)
print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))
