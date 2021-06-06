All of your source code (and other program resources) should be placed in this sub-directory. The source durectory us split into 3 sections
* generation of dat
we will create functions to baseline model, and compare it to a reference model. this is achieved by hashing the model strycture, andvthen each of the layers
an example of transfer learning will take place, and at each major change (a certain amount of delta), then a new baseline us created, with a pointer to the orevious model
once a model is ready for oroduction, ut will create its full delta with theoriginal model, and a pointer to its hash
the next question is can we identify the originnofvthe model being deployed. this is a test that shows the lifecycle of model creation ata lical level, and parentage of the model at a glibal level
thecthird part is visualisation of the difdrrence - showing hos the model evolved, anc for released models, a path to their origin.
*



*
