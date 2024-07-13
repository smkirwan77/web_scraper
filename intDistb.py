def int2(string):
                       
    dist = string
    dist = string.split('(')[0].strip()
    if "m" in dist:
        m, r = int(dist.split('m')[0]), dist.split('m')[1]
        if "f" in dist and "yd" in dist:
            f, r = int(r.split('f')[0]), r.split('f')[1]
            y = int(r.split('yd')[0])
            
        elif "f" in dist:
            y = 0
            f = int(r.split('f')[0])
        elif "yd" in dist:
            f = 0
            y = int(r.split('yd')[0])
        else:
            f = 0
            y = 0        
        
    else:
        m = 0
        if "f" in dist and "yd" in dist:
            f, y = int(dist.split('f')[0]), int(dist.split('f')[1].replace('yds',''))
            
        else:
            y = 0
            f = int(dist.replace("f", ""))
     
    race_dist = 8*m + f + y/220
    return round(race_dist,2)    
        
def get_intDists(string):    
    
    furlongs_per_unit = {"y": 1/220, "m": 8, "f": 1}

    m_f = ["m", "f"]
    f_y = ["f", "y"]
    m_y = ["m", "y"]
    
    dist_string = string
    dist_list = dist_string.split()
    
    
    if len(dist_list) == 3:
        dist_list = dist_string.split()
        
        mi, fu, ya = dist_list
        
    else:
        if len(dist_list) == 2:
            if all(x in dist_string for x in m_f):
                dist_list.append("0y")
            
                mi, fu, ya = dist_list
                
            else:
                if all(x in dist_string for x in f_y):
                    dist_list.append("0m")
                    fu, ya, mi = dist_list
            
                else:
                    if all(x in dist_string for x in m_y):
                        dist_list.append("0f")
                        mi, ya, fu = dist_list
    
            #mi, fu, ya = dist_list
            
        else:
            if len(dist_list) == 1:
                if "m"  in dist_string:
                    dist_list.append("0f")
                    dist_list.append("0y")
                    mi, ya, fu = dist_list               
                       
    
                else:    
                    dist_list.append("0m")
                    dist_list.append("0y")
                    fu, mi, ya  = dist_list               
    
    return round(float(mi[:-1]) * furlongs_per_unit[mi[-1]] + float(fu[:-1]) * furlongs_per_unit[fu[-1]] + float(ya[:-1]) * furlongs_per_unit[ya[-1]],2)

def getY(string):
    furlongs_per_unit = {"y": 1, "m": 8*220, "f": 220}

    m_f = ["m", "f"]
    f_y = ["f", "y"]
    m_y = ["m", "y"]
    
    dist_string = string
    dist_list = dist_string.split()
    
    
    if len(dist_list) == 3:
        dist_list = dist_string.split()
        
        mi, fu, ya = dist_list
        
    else:
        if len(dist_list) == 2:
            if all(x in dist_string for x in m_f):
                dist_list.append("0y")
            
                mi, fu, ya = dist_list
                
            else:
                if all(x in dist_string for x in f_y):
                    dist_list.append("0m")
                    fu, ya, mi = dist_list
            
                else:
                    if all(x in dist_string for x in m_y):
                        dist_list.append("0f")
                        mi, ya, fu = dist_list
    
            #mi, fu, ya = dist_list
            
        else:
            if len(dist_list) == 1:
                if "m"  in dist_string:
                    dist_list.append("0f")
                    dist_list.append("0y")
                    mi, ya, fu = dist_list               
                       
    
                else:    
                    dist_list.append("0m")
                    dist_list.append("0y")
                    fu, mi, ya  = dist_list               
    
    return int((float(mi[:-1]) * furlongs_per_unit[mi[-1]] + float(fu[:-1]) * furlongs_per_unit[fu[-1]] + float(ya[:-1]) * furlongs_per_unit[ya[-1]]))

def intY(string):
                       
    dist = string
    if "m" in dist:
        m, r = int(dist.split('m')[0]), dist.split('m')[1]
        if "f" in dist and "yd" in dist:
            f, r = int(r.split('f')[0]), r.split('f')[1]
            y = int(r.split('yd')[0])
            
        elif "f" in dist:
            y = 0
            f = int(r.split('f')[0])
        elif "yd" in dist:
            f = 0
            y = int(r.split('yd')[0])
        else:
            f = 0
            y = 0        
        
    else:
        m = 0
        if "f" in dist and "yd" in dist:
            f, y = int(dist.split('f')[0]), int(dist.split('f')[1].replace('yds',''))
            
        else:
            y = 0
            f = int(dist.replace("f", ""))
     
    race_dist_y = 8*m*220 + f*220 + y
    race_dist_f = 8*m + f + y/220
    
    return round(race_dist_y,2), round(race_dist_f,2)   