import utils

#fn="aidaArticles.tsv"
#fn="aidaTopLevel.tsv"
fn="aidaSingleArticles.tsv"
#fn="aidaLowLevel.tsv"
print("########################### MY SYSTEM ######################")
p, r, f=utils.computeStats(fn, False)
print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))

print("########################### MY SYSTEM (NO REREAD) ######################")
p, r, f=utils.computeStats("noreread." + fn, False)
print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))

print("########################### AGDISTIS ######################")
p, r, f=utils.computeStats(fn, True)
print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))
