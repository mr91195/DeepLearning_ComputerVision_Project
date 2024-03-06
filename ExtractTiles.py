from osgeo import ogr, gdal, osr
from shapely.geometry import LineString, Point, Polygon
from shapely import wkt
import math
from PIL import Image
import cv2
Image.MAX_IMAGE_PIXELS = 10000000000000



#Set path elevation.shp
inputshp_path = r"C:\Users\MR911\OneDrive\Desktop\Uni 3.0\1° Anno\Codice di R. Minervini\File_ExtractTiles\elevation.shp"

chaintickshp_path = r"C:\Users\MR911\OneDrive\Desktop\Uni 3.0\1° Anno\Codice di R. Minervini\File_ExtractTiles.2\output_lines.shp"





def create_ticks(shp_path,distance):

    ## set the driver for the data
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ## open the Shapefile in write mode (1)
    ds = driver.Open(shp_path, 1)

    inputshp = ogr.Open(shp_path)
    lyr = inputshp.GetLayer()

    ## linear feature class
    input_lyr_name = "output"

    ## distance between points
    #distance = 1
    ## the length of each tick
    #tick_length = 5

    ## output tick line fc name
    #output_lns = "{0}_{1}m_lines".format(input_lyr_name, distance)
    output_lns = "{0}_lines".format(input_lyr_name)

    ## list to hold all the point coords
    list_points = []

    ## reference the layer using the layers name
    if input_lyr_name in [ds.GetLayerByIndex(lyr_name).GetName() for lyr_name in range(ds.GetLayerCount())]:
        lyr = ds.GetLayerByName(input_lyr_name)
        print ("{0} found in {1}".format(input_lyr_name, shp_path))

    ## if the output already exists then delete it
    if output_lns in [ds.GetLayerByIndex(lyr_name).GetName() for lyr_name in range(ds.GetLayerCount())]:
        ds.DeleteLayer(output_lns)
        print ("Deleting: {0}".format(output_lns))

    ## create a new line layer with the same spatial ref as lyr
    out_ln_lyr = ds.CreateLayer(output_lns, lyr.GetSpatialRef(), ogr.wkbLineString)

    ## distance/chainage attribute
    chainage_fld = ogr.FieldDefn("CHAINAGE", ogr.OFTReal)
    id_fld = ogr.FieldDefn("ID", ogr.OFTInteger)
    out_ln_lyr.CreateField(chainage_fld)
    out_ln_lyr.CreateField(id_fld)
    ## check the geometry is a line
    first_feat = lyr.GetFeature(0)

    ## accessing linear feature classes using FileGDB driver always returns a MultiLinestring
    if first_feat.geometry().GetGeometryName() in ["LINESTRING", "MULTILINESTRING"]:
        for ln in lyr:
            ## list to hold all the point coords
            list_points = []
            ## set the current distance to place the point
            current_dist = distance
            ## get the geometry of the line as wkt
            line_geom = ln.geometry().ExportToWkt()
            ## make shapely LineString object
            #shapely_line = MultiLineString(wkt.loads(line_geom))
            shapely_line = LineString(wkt.loads(line_geom))
            #print(shapely_line)
            ## get the total length of the line
            line_length = shapely_line.length
            #print(line_length)
            ## append the starting coordinate to the list
            #list_points.append(Point(list(shapely_line[0].coords)[0]))
            list_points.append(Point(list(shapely_line.coords)[0]))
            ## https://nathanw.net/2012/08/05/generating-chainage-distance-nodes-in-qgis/
            ## while the current cumulative distance is less than the total length of the line
            while current_dist < line_length:
                ## use interpolate and increase the current distance
                list_points.append(shapely_line.interpolate(current_dist))
                current_dist += distance
            ## append end coordinate to the list
            #list_points.append(Point(list(shapely_line[0].coords)[-1]))
            list_points.append(Point(list(shapely_line.coords)[-1]))

            ## add lines to the layer
            ## this can probably be cleaned up better
            ## but it works and is fast!

            #Set path rgb
            im = Image.open(r"C:\Users\MR911\OneDrive\Desktop\Uni 3.0\1° Anno\Codice di R. Minervini\File_ExtractTiles\nuovoCantiereRGB.tif")
            filename = r"C:\Users\MR911\OneDrive\Desktop\Uni 3.0\1° Anno\Codice di R. Minervini\File_ExtractTiles\nuovoCantiereRGB.tif"
            dataset = gdal.Open(filename)
            


            transform = dataset.GetGeoTransform()

            print (transform)


            
            
            for num, pt in enumerate(list_points, 1):
                ## start chainage 0
                '''if num == 1:
                    angle = getAngle(pt, list_points[num])
                    line_end_1 = getPoint1(pt, angle, tick_length/2)
                    angle = getAngle(line_end_1, pt)
                    line_end_2 = getPoint2(line_end_1, angle, tick_length)
                    tick = LineString([(line_end_1.x, line_end_1.y), (line_end_2.x, line_end_2.y)])
                    feat_dfn_ln = out_ln_lyr.GetLayerDefn()
                    feat_ln = ogr.Feature(feat_dfn_ln)
                    feat_ln.SetGeometry(ogr.CreateGeometryFromWkt(tick.wkt))
                    feat_ln.SetField("CHAINAGE", 0)
                    feat_ln.SetField("ID", 0)
                    out_ln_lyr.CreateFeature(feat_ln)'''

                ## everything in between
                if num < len(list_points) - 1:

                    '''
                    angle = getAngle(pt, list_points[num])
                    line_end_1 = getPoint1(list_points[num], angle, tick_length/2)
                    angle = getAngle(line_end_1, list_points[num])
                    line_end_2 = getPoint2(line_end_1, angle, tick_length)
                    tick = LineString([(line_end_1.x, line_end_1.y), (line_end_2.x, line_end_2.y)])
                    feat_dfn_ln = out_ln_lyr.GetLayerDefn()
                    feat_ln = ogr.Feature(feat_dfn_ln)
                    feat_ln.SetGeometry(ogr.CreateGeometryFromWkt(tick.wkt))
                    feat_ln.SetField("CHAINAGE", distance * num)
                    feat_ln.SetField("ID", num)
                    out_ln_lyr.CreateFeature(feat_ln)
                    
                    '''
                    xy = list_points[num].coords
                    x = xy[0]
                    xmin = x[0] - 2 
                    xmax = x[0] + 2
                    ymin = x[1] - 2
                    ymax = x[1] + 2
                    point1 = Point(xmin,ymin)
                    point2 = Point(xmin,ymax)
                    point3 = Point(xmax,ymax)
                    point4 = Point(xmax,ymin)

                    pointlist = [point1, point2,point3,point4,point1]
          
                    poligono = Polygon([[p.x, p.y] for p in pointlist])
                    
                    #angle = getAngle(pt, list_pointtakes from 1 to 3 positional arguments but 6 were givens[num])
                    #line_end_1 = getPoint1(list_points[num], angle, tick_length/2)
                    #angle = getAngle(line_end_1, list_points[num])
                    #line_end_2 = getPoint2(line_end_1, angle, tick_length)
                    #tick = LineString([(point1.x , point1.y ), (point2.x , point2.y ), (point3.x , point3.y ), (point4.x , point4.y )])
                    feat_dfn_ln = out_ln_lyr.GetLayerDefn()
                    feat_ln = ogr.Feature(feat_dfn_ln)
                    feat_ln.SetGeometry(ogr.CreateGeometryFromWkt(poligono.wkt))
                    feat_ln.SetField("CHAINAGE", distance * num)
                    feat_ln.SetField("ID", num)
                    out_ln_lyr.CreateFeature(feat_ln)

                    
                    #array num senza rete
                    '''
                    norete = [100, 120, 154, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 
                            168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 198, 201, 202, 
                            204, 255, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 
                            310 ,311, 312, 313, 314, 315, 316, 317, 318, 319, 320 , 321, 322, 323]
                    '''
                    #volo num 8(nuovaCartella)
                    '''
                    norete = [14, 30, 31, 43, 44, 45, 46, 47, 48, 49, 52, 53, 54, 55, 127, 162,165, 166, 167, 186, 200, 235, 236,
                             237, 260, 287, 288, 290, 301, 302, 336, 344, 345, 427, 428, 429, 435, 454, 455, 456, 457, 471, 477, 478]
                    '''

                    #trasform a coord in pixel
                    
                    p1 = (xmin , ymax)
                    p2 = (xmax , ymin)

                    xOrigin = transform[0]
                    yOrigin = transform[3]
                    pixelWidth = transform[1]
                    pixelHeight = -transform[5]
                    print (xOrigin, yOrigin)

                    i1 = int((p1[0] - xOrigin) / pixelWidth)
                    j1 = int((yOrigin - p1[1] ) / pixelHeight)
                    i2 = int((p2[0] - xOrigin) / pixelWidth)
                    j2 = int((yOrigin - p2[1]) / pixelHeight)

                    print (i1, j1)
                    print (i2, j2)
                    im1 = im.crop((i1, j1, i2, j2))

                    name = str(num)
                    # save a patch


                    '''
                    if num in norete:

                        path1 = r"C:\Users\MR911\OneDrive\Desktop\Uni 3.0\1° Anno\Codice di R. Minervini\patchUltimoCantiere\no_rete"
                        path2 = ".tif"

                        im1.save(path1 +"\\"+ name + path2) # saves the image
                        num_no_rete += 1

                    else:
                        
                        path1 = r"C:\Users\MR911\OneDrive\Desktop\Uni 3.0\1° Anno\Codice di R. Minervini\patchUltimoCantiere\rete"
                        path2 = ".tif"
                        im1.save(path1 +"\\"+ name + path2) # saves the image
                        num_rete += 1
                    '''
    del ds            



create_ticks(inputshp_path, 4)
