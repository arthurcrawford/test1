
##Examples

Create a repository

    raptly create pizza/pizza4/trusty    
    
Publish / re-publish the unstable distribution 

    raptly deploy pizza/pizza4/trusty
    
Deploy a package and publish / re-publish the unstable distribution    

    raptly deploy pizza/pizza4/trusty margherita_1.0.0_all.deb
    
Show packages in the unstable distribution

    raptly show pizza/pizza4/trusty unstable
    
Create a test candidate comprising all packages from stable distribution (none yet) plus packages from unstable that 
match the query

    raptly test pizza/pizza4/trusty --packages "margherita_1.0.0_all " TKT-1234
    
Stage the test candidate in the staging distribution    
    
    raptly stage pizza/pizza4/trusty TKT-1234
    
Release the test candidate to the stable distribution

    raptly release pizza/pizza4/trusty TKT-1234
    
Show how the whole repository is constituted 

    raptly show pizza/pizza4/trusty
    
    
TODO    
Create a check distribution for development testing

    raptly check pizza/pizza4/trusty --packages "margherita"


## Command Reference

### check

The primary use case for the  `check` command is to check that your new changes will work with reference to the 
stable distribution.  This is illustrated below.

    raptly check pizza mozzarella_1.5.3-dev_all.deb
    
    pool                       pizza.check.<myuser>.<timestamp>.<uuid>   stable
    ========                   =======================================   ======
    mozzarella_1.5.3-dev_all   ++>    mozzarella_1.5.3-dev_all           mozzarella_1.5.2_all                                                                          
    [...]                             fiorentina_1.0.2_all         <<<   fiorentina_1.0.2_all                                    
                                      margherita_1.0.0_all         <<<   margherita_1.0.0_all                                
                                      meatfeast_99.1.5_all         <<<   meatfeast_99.1.5_all

In the example, a new development version of the package `mozzarella` has been created for the `pizza` repository.  
The `raptly check` command is then invoked. The new package is first uploaded to the aptly server's *pool* and then 
a new `check` repo distribution is published.  The name of the distribution is formed by taking the repo name and 
appending to it the word check followed by the client's username, a timestamp and unique ID.  The newly published 
check distribution consists of the current `stable` distribution *plus* the new version of the package in question.  

The `check` distribution is used to check that the code works in integration with all the other packages 
in the stable distribution - i.e. the current production code.  Typically, a full development stack will be created
from a given`check` distribution. 

By supplying the `--checks` argument to the `raptly show <repo name>`, you can see the official set of distributions
in addition to any check distributions you have created.

    raptly show pizza --checks
    
    Distributions:
      stable -> pizza.TKT-1234.1506701691
      staging -> pizza.TKT-1234.1506701691
      testing -> pizza.TKT-1234.1506701691
      unstable -> pizza.1507039393
      
    Checks:
      pizza.check.artcrawford.1507139048.60c74ae9
      pizza.check.artcrawford.1507238038.51e529a6
  
To manage the proliferation of `check` distributions you should delete those you no longer want.  This is to save 
disk space, since every published distribution is a signed *copy* of all the binary packages in the distribution which 
occupies significant disk space.

To delete an individual check distribution.

    raptly check --delete check.artcrawford.1507139048.60c74ae9
    
To delete all your check distributions.
    
    raptly check --clean


### deploy

The `deploy` command is used to formally 

### test    

The following example shows how a testing candidate is constructed. 

    raptly test pizza/pizza4/trusty --packages "margherita_1.1.0-beta_all|fiorentina_0.9.7_all" TKT-8904
 
    unstable                        testing                          stable
    ========                        =======                          ======
    fiorentina_0.9.7_all       >>>  fiorentina_0.9.7_all  
    fiorentina_1.0.0_all            
    fiorentina_1.0.1-beta_all       
    fiorentina_1.0.2_all            
    margherita_1.0.0_all            margherita_1.0.0_all       <<<   margherita_1.0.0_all
    margherita_1.1.0_all            
    margherita_1.1.0-2_all          
    margherita_1.1.0-beta_all  >>>  margherita_1.1.0-beta_all  
    
The stable distribution contains the single package `margherita_1.0.0_all`.  The `--packages` selection argument to the 
`test` command specifies two additional packages to be drawn into the test candidate from unstable.  This results in a 
testing candidate that contains the union of all three packages.

Note - if any of the packages specified in the `--packages` selection argument are not present in unstable, an error is 
reported.



        
    