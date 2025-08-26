# jobs
jobs = {
    '1': {"a" : {"actions": ["input", "print_A4", "bind_A4", "output"], 
               "machines" : [{"M" : [0, 1, 4, 5],   # machines per action
                              "P" : [0, 4, 3, 0],   # processing time per action
                              "W" : [0, 0, 2, 0]    # delay before being able to start action
                            },
                            { "M" : [0, 2, 4, 5],   # machines per action
                              "P" : [0, 6, 3, 0],   # processing time per action
                              "W" : [0, 0, 4, 0]    # delay before being able to start action
                            }]
               },
        "b" : {"actions": ["input", "print_A3", "snij_A3", "bind_A4", "output"], 
               "machines" : [{"M" : [0, 2, 3, 4, 5],   # machines per action
                              "P" : [0, 3, 3, 3, 0],   # processing time per action
                              "W" : [0, 0, 1, 2, 0]    # delay before being able to start action
                            }]
               }
    },
    '2': {"a" : {"actions": ["input", "print_A4", "output"], 
               "machines" : [{"M" : [0, 2, 5],   # machines per action
                              "P" : [0, 4, 0],   # processing time per action
                              "W" : [0, 1, 0]    # delay before being able to start action
                            },
                            { "M" : [0, 2, 5],   # machines per action
                              "P" : [0,10, 0],   # processing time per action
                              "W" : [0, 0, 0]    # delay before being able to start action
                            }]
               },
    },
    '3': {"a" : {"actions": ["input", "print_A3", "snij_A3", "bind_A4", "output"], 
               "machines" : [{"M" : [0, 2, 3, 4, 5],   # machines per action
                              "P" : [0, 5, 4, 3, 0],   # processing time per action
                              "W" : [0, 0, 2, 2, 0]    # delay before being able to start action
                            }]
               },
    },
    '4': {"a" : {"actions": ["input", "print_A4", "bind_A4", "snij_A3", "output"], 
               "machines" : [{"M" : [0, 1, 4, 3, 5],   
                              "P" : [0, 6, 2, 3, 0],   
                              "W" : [0, 0, 1, 2, 0]    
                            },
                            { "M" : [0, 1, 4, 3, 5],   
                              "P" : [0, 5, 3, 2, 0],   
                              "W" : [0, 1, 0, 3, 0]    
                            }]
               },
        "b" : {"actions": ["input", "print_A3", "bind_A4", "output"], 
               "machines" : [{"M" : [0, 2, 4, 5],   
                              "P" : [0, 4, 3, 0],   
                              "W" : [0, 0, 2, 0]    
                            },
                            { "M" : [0, 2, 4, 5],   
                              "P" : [0, 5, 2, 0],   
                              "W" : [0, 2, 1, 0]    
                            }]
               }
    },
    '5': {"a" : {"actions": ["input", "print_A4", "bind_A4", "output"], 
               "machines" : [{"M" : [0, 1, 4, 5],   
                              "P" : [0, 3, 4, 0],   
                              "W" : [0, 0, 1, 0]    
                            },
                            { "M" : [0, 2, 4, 5],   
                              "P" : [0, 5, 5, 0],   
                              "W" : [0, 1, 2, 0]    
                            }]
               },
        "b" : {"actions": ["input", "print_A4", "bind_A4", "print_A4", "output"], 
               "machines" : [{"M" : [0, 2, 4, 1, 5],  
                              "P" : [0, 4, 3, 2, 0],   
                              "W" : [0, 1, 1, 0, 0]    
                            },
                            { "M" : [0, 1, 4, 1, 5],  
                              "P" : [0, 6, 2, 3, 0],   
                              "W" : [0, 0, 2, 1, 0]    
                            }]
               }
    }
}