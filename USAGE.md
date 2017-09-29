
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



        
    