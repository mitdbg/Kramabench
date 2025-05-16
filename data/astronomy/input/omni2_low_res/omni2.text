                              O M N I 2  DATA SET
                                             
  The  /data/omni/low_res_omni/ directory contains the hourly mean values of 
  the interplanetary magnetic  field (IMF) and solar wind plasma parameters 
  measured by various spacecraft near  the  Earth's  orbit,  as  well  as  
  geomagnetic and solar activity indices, and energetic proton fluxes
  known as OMNI2 data. 

  OMNI2 was created at NSSDC in 2003 as a successor to the OMNI data set 
  first created in the mid-1970's.  
                   
  Time spans of various parameters are periodically extended.
   The documentation file at
    https://omniweb.gsfc.nasa.gov/html/ow_data.html
    gives the current time spans of the following parameter groups:
    Magnetic field
    Plasma
    Kp index and sunspot number
    AE, AL,AU index
    Provisional AE, AL, AU index
    Quick look AE, AL, AU index
    Dst index
    Provisional Dst index
    Quick look Dst
    Energetic proton fluxes
    ap-index and f10.7_index
    PC(N) index
 ---------------
 Note: see "extended" directoty for more parameters.
 ----------------------------------------------
 
  Data gaps were filled with dummy numbers for the missing hours or entire
  days to make all files of equal length.  The character '9' is used to
  fill all fields for missing data according to their format, e.g.
  ' 9999.9' for a field with the FORTRAN format F7.1. Note that format F7.1
  below really means (1X,F6.1),etc.

  This directory  includes  two types of the ASCII flat files: OMNI2_YYYY.DAT, 
  and OMNI_MYYYY.DAT  where  YYYY  is  a given year. The OMNI2_YYYY.DAT files 
  contain the original data where  the  IMF  and solar wind velocity vectors 
  are presented in GSE and, for IMF, GSM coordinate  systems.  The modified 
  OMNI_MYYYY.DAT files have been  created  from  these  files with reformatting 
  for COHOWeb compatibility and with the  IMF and velocity 
  vectors having been transformed to  RTN coordinate system. 
                            
--------------------------------------------------------------------------- 

Daily and 27-day Averages files: omni_01_av.dat; omni_27_av.dat; omni_m_daily.dat

We have computed daily and 27-day average values for all the OMNI parameters in the
OMNI2_YYYY.dat files, and we have computed daily averages from the OMNI_MYYYY.dat files.
We have made these lower resolution averages also accessible via OMNIWeb and via anon/ftp.
Only arithmetic averaging was done.  (No averaging of logarithms.)  No threshold numbers 
of finer scale points were required.


The daily averages are taken over OMNI's basic hourly values, and the 27-
day averages are taken over the daily averages.  The corresponding standard 
deviations relate only to these averagings and do not capture the 
variances in the higher resolution data.

The 27-day averages are for discrete Bartels rotation numbers.  Thus the 
first such average fully within 1999 spans January 9 through February 4.

The record format for the daily and 27-day averages is the same as for the 
hourly data, although certain fields have special meanings.

The time words (year, day, hour) correspond to the first hour of the 
average.

The ID's for the magnetic field and plasma spacecraft are set to zero, 
since the daily and 27-day averages frequently involve data from multiple 
spacecraft.

The numbers of fine scale points in the plasma and field averages are 
counts of (1) hourly values contributing to daily averages or (2) daily 
values contributing to 27-day averages.  NOTE THAT WE HAVE NOT REQUIRED ANY 
MINIMUM NUMBER OF POINTS TO COMPUTE AN AVERAGE.  For cases where there was 
only one point, the standard deviations were set to zero.

Kp was treated specially.  After determining daily or 27-averages from 
basic values such as 10 (1), 13 (1+), 17 (2-), 20 (2), the average was 
rounded to the nearest "standard value" of Kp (i.e., 10, 13, 17, 20, ...).  
For cases where the average was exactly in the middle between standard 
values (e.g., 15), the lower standard value (13 in this case) was used.
-------------------------------------------------------------------------
 
     


                         OMNI2_YYYY.DAT FORMAT DESCRIPTION     
                                                   
         
WORD  FORMAT  Fill Value         MEANING                  UNITS/COMMENTS
                               
 1      I4              Year                              1963, 1964, etc.
 2      I4              Decimal Day                       January 1 = Day 1
 3      I3              Hour                              0, 1,...,23   
 4      I5   9999      Bartels rotation number
 5      I3    99        ID for IMF spacecraft             See table
 6      I3    99        ID for SW plasma spacecraft       See table
 7      I4   999       # of points in the IMF averages 
 8      I4   999       # of points in the plasma averages 
 9     F6.1  999.9     Field Magnitude Average |B|       1/N SUM |B|, nT
10     F6.1  999.9     Magnitude of Average Field Vector sqrt(Bx^2+By^2+Bz^2) 
11     F6.1  999.9     Lat.Angle of Aver. Field Vector   Degrees (GSE coords) 
12     F6.1  999.9     Long.Angle of Aver.Field Vector   Degrees (GSE coords) 
13     F6.1  999.9     Bx GSE, GSM                       nT 
14     F6.1  999.9     By GSE                            nT 
15     F6.1  999.9     Bz GSE                            nT 
16     F6.1  999.9     By GSM                            nT
17     F6 1  999.9     Bz GSM                            nT
                                                      see  http://geo.phys.spbu.ru/~tsyganenko/Geopack-2008.html 
                                                          developed by Drs. Nikolai Tsyganenko. 

18     F6.1  999.9     sigma|B|            RMS Standard Deviation in average
                                               magnitude (word 10), nT
19     F6.1  999.9     sigma B             RMS Standard Deviation in field
                                            vector, nT (**)
20     F6.1  999.9     sigma Bx            RMS Standard Deviation in GSE 
                                            X-component average, nT 
21     F6.1  999.9     sigma By            RMS Standard Deviation in GSE
                                            Y-component average, nT 
22     F6.1  999.9     sigma Bz            RMS Standard Deviation in GSE 
                                             Z-component average, nT 

23     F9.0  9999999.  Proton temperature                Degrees, K
24     F6.1  999.9     Proton Density                    N/cm^3 

25     F6.0  9999.     Plasma (Flow) speed               km/s
26     F6.1  999.9     Plasma Flow Long. Angle    Degrees, quasi-GSE*
27     F6.1  999.9     Plasma  Flow Lat. Angle     Degrees, GSE* 

28     F6.3  9.999     Na/Np                    Alpha/Proton ratio 
29     F6.2  99.99     Flow Pressure            P (nPa) = (1.67/10**6) * Np*V**2 * (1+ 4*Na/Np)
                                                for hours with non-fill Na/Np ratios and
                                                P (nPa) = (2.0/10**6) * Np*V**2
                                                for hours with fill values for Na/Np

30     F9.0  9999999.  sigma T                           Degrees, K
31     F6.1  999.9     sigma N                           N/cm^3
32     F6.0  9999.     sigma V                           km/s
33     F6.1  999.9     sigma phi V                       Degrees
34     F6.1  999.9     sigma theta V                     Degrees
35     F6.3  9.999     sigma-Na/Np   

36     F7.2  999.99    Electric field         -[V(km/s) * Bz (nT; GSM)] * 10**-3. (mV/m)
37     F7.2  999.99    Plasma beta            Beta = [(T*4.16/10**5) + 5.34] * Np / B**2
38     F6.1  999.9     Alfven mach number      Ma = (V * Np**0.5) / 20 * B



39     I3    99        Kp               Planetary Geomagnetic Activity Index
                                       (e.g. 3+ = 33, 6- = 57, 4 = 40, etc.)

40      I4   999        R                          Sunspot number (new version 2)
41      I6   99999     DST Index                    nT, from Kyoto 
42      I5   9999      AE-index                    nT, from Kyoto
43     F10.2 999999.99 Proton flux                 number/cmsq sec sr >1 Mev 
44     F9.2  99999.99  Proton flux                 number/cmsq sec sr >2 Mev
45     F9.2  99999.99  Proton flux                 number/cmsq sec sr >4 Mev
46     F9.2  99999.99  Proton flux                 number/cmsq sec sr >10 Mev
47     F9.2  99999.99  Proton flux                 number/cmsq sec sr >30 Mev
48     F9.2  99999.99  Proton flux                 number/cmsq sec sr >60 Mev
49      I3   0         Flag(***)                       (-1,0,1,2,3,4,5,6)     
 
50       I4   999      ap-index                     nT
51       F6.1 999.9    f10.7_index                  ( sfu = 10-22W.m-2.Hz-1)
52       F6.1 999.9    PC(N) index
53       I6   99999    AL-index, from Kyoto         nT                  
54       I6   99999    AU-index, from Kyoto         nT
55       F5.1  99.9   Magnetosonic mach number= = V/Magnetosonic_speed
                     Magnetosonic speed = [(sound speed)**2 + (Alfv speed)**2]**0.5
                     The Alfven speed = 20. * B / N**0.5 
                     The sound speed = 0.12 * [T + 1.28*10**5]**0.5 
                   About Magnetosonic speed check  http://ftpbrowser.gsfc.nasa.gov/bow_derivation1.html also
 --------------------------------------------------------------------------------------------------                
                                C O M M E N T S 

   (*)   Quasi-GSE for the flow longitude angle means the angle increases from zero
         to positive values as the flow changes from being aligned along the -X(GSE)
         axis towards the +Y(GSE) axis.  The flow longitude angle is positive for 
         flow from west of the sun, towards +Y(GSE).
         The flow latitude angle is positive for flow from south of the sun, 
         towards +Z(GSE)
                       
   (**) - sigma B is sqrt((sigma Bx)^2 + (sigma By)^2 +(sigma Bz)^2)
                          
  (***) - If the flag is 0 there are no Proton Flux data, or all of the
          Proton Flux data are contaminated by the magnetospheric events
                     
          If the flag is 1 then the channels >1,>2,>4,>10,>30 Mev were
          judged to have magnetospheric `contamination'
                    
          If the flag is 2 then the channels >1,>2,>4,>10 Mev were judged
          to have magnetospheric `contamination'
                              
          If the flag is 3 then the channels>1,>2,>4 Mev were judged to 
          have magnetospheric `contamination'
                            
          If the flag is 4 then the channels >1,>2 Mev were judged to have
          magnetospheric `contamination'
                          
          If the flag is 5 then the channels >1 Mev channels were judged to
          have magnetospheric `contamination'
                          
          If the flag is 6 then no channel was judged to have magnetospheric
          `contamination'

           If the flag is -1 then data were not checked for magnetospheric
           contamination; this is relevant after 1988/306.

         
              
                         TABLE: SPACECRAFT IDENTIFIERS 
                    
       Spacecraft Name                                    Spacecraft ID
                            
       IMP 1 (Explorer 18)                                      18
       IMP 3 (Explorer 28)                                      28    
       IMP 4 (Explorer 34)                                      34
       IMP 5 (Explorer 41)                                      41    
       IMP 6 (Explorer 43)                                      43
    
       IMP 7 (Explorer 47)                                      47 MAG and Plasma/MIT
       IMP 7 (Explorer 47)                                      44 Plasma/LANL

       IMP 8 (Explorer 50)                                     50 MAG and Plasma/MIT
       IMP 8 (Explorer 50)                                     45 Plasma/LANL
      
       AIMP 1 (Explorer 33)                                     33    
       AIMP 2 (Explorer 35)                                     35   
       HEOS 1 and HEOS 2                                         1
       VELA 3                                                    3
       OGO 5                                                     5
       Merged LANL VELA Speed Data (July 1964 - March 1971)     97
       Merged LANL IMP T,N,V (Including all IMP 8 LANL Plasma)  98
       ISEE 1                                                   11
       ISEE 2                                                   12
       ISEE 3                                                   13
       PROGNOZ 10                                               10
       WIND                                                     51 -mag, plasma_KP; 52-Plasma_definitive
       ACE                                                      71 
       Geotail                                                  60
       No spacecraft                                            99
                  
   ---------------------------------------------------------------------------------               
 

                       
                          OMNI_MYYYY.DAT FORMAT DESCRIPTION
                                                          
  Logical record = 82 characters + CR/LF  
                  
WORD  FORMAT FILL Value   MEANING                     UNITS/COMMENTS
                
1       I4                Year                              1963, 1964, 1965, etc.
2       I4                Decimal Day                       January 1 = Day 1  
3       I3                Hour                              0,1,...,23 
4      F7.1  9999.9       Heliographic Inertial Latitude    Degrees, +/-90
                          of the Earth 
5      F7.1  9999.9       Heliographic Inertial Longitude   Degrees, 0-360
                          of the Earth 
6      F6.1  999.9        BR RTN                            nanoteslas
7      F6.1  999.9        BT RTN                            nanoteslas
8      F6.1  999.9        BN RTN                            nanoteslas
9      F6.1  999.9        Field Magnitude Average |B        1/N SUM |B|, nT
10     F6.0  9999.        Bulk Flow speed                   km/s
11     F6.1  999.9       THETA - elevation angle           Degrees        
                          of the velocity vector (RTN) 
12     F6.1  999.9       PHI- azimuth angle                Degrees
                          of the velocity vector (RTN) 
13     F6.1  999.9        Proton Density                       N/cm^3
14     F9.0  9999999.     Temperature                       Degrees, K   
                
                      
                  DESCRIPTION OF COORDINATE SYSTEMS
 
  The Heliographic Inertial (HGI) coordinates are Sun-centered and inertially
  fixed with respect to an X-axis directed along the intersection line of the
  ecliptic and solar equatorial  planes. The solar equator plane is inclined
  at 7.25 degrees from the ecliptic. This direction was towards ecliptic 
  longitude of 74.367 degrees  on  1  January  1900  at  1200  UT; because of
  precession of the celestial  equator, this longitude increases by 1.4 
  degrees/century. The Z axis  is  directed perpendicular and northward from 
  the solar equator, and the  Y-axis  completes  the right-handed set. This 
  system differs from the usual  heliographic  coordinates  (e.g.  Carrington
  longitudes) which are fixed in the frame of the rotating Sun. 

  The RTN system is fixed at a spacecraft (or the planet). The R  axis 
  is directed radially away from the Sun, the T axis is the cross product of 
  the solar rotation axis and  the  R  axis,  and  the  N  axis is the cross 
  product of the R  and  T  axes.  At  zero  heliographic latitude, when the 
  spacecraft is in the solar equatorial plane, the N and solar rotation axes 
  are parallel.
                      
  --------------------------------------------------------------------------
                 Convention for Latitude and Longitude Angles
  --------------------------------------------------------------------------
                                                       
  Latitude  and  longitude  angles  of  solar wind plasma flow are generally
  measured  from the radius vector away from the Sun. In all cases, latitude
  angles  are  positive for north-going flow. The flow longitude angles have
  been  treated differently for the near-Earth data, i.e. the OMNI, and for 
  the deep space data. The flow is positive for  the  near-Earth  data  when
  coming from the right side of the Sun as viewed  from  the Earth, i.e. 
  flowing toward +Y from -X GSE or opposite to the  direction of planetary 
  motion. On the other hand, the flow longitudes for the deep space spacecraft
  use the opposite sign convection, i.e. positive for flow in the +T direction
  in the RTN system.
                                    
  --------------------------------------------------------------------------
Related data and directories:
SPDF Data and Orbits Services <http://spdf.gsfc.nasa.gov/>

-------------------------------------------
  Acknowledgement:

 Use of these data in publications should be accompanied by
 acknowledgements of the 
Space Physics Data Facility(SPDF) and
-------------------------------------------------------------------------
SPDF Contact: Natalia Papitashvili <Natalia.E.Papitashvili@nasa.gov>

---------------------------------------------------------------------------
Authorizing NASA Official:  R.M. Candey, Head, SPDF, NASA Goddard Space Flight Center
                        e-mail:  Robert.m.candey@nasa.gov
-----------------------------------------------------------------
___________________________________________________________________________________