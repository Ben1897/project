import rdflib

def semanticUnitConversion(unit1ele, unit2ele):
    '''
    Semantically convert the units of input to the standard units parsed
    from the semantic contents of the symbols and return the coefficient of it
    Note: based on SWEET ontology
    '''
    # ... load SWEET unit ontology
    g = rdflib.Graph()
    #g.parse(r'D:\researchInUIUC\project\Ontologies\Green_Ampt3.owl')
    g.parse(r'C:\Users\Ben1897\Desktop\SWEET_rdf_edit.owl')
    # ... find all units with symbols for mapping
    symbol = g.query(
    """SELECT DISTINCT ?a ?b
       WHERE {
          ?a screla:hasSymbol ?b .
          ?a rdf:type ?c .
          FILTER ( (?c != <http://sweet.jpl.nasa.gov/2.3/reprSciUnits.owl#Prefix>) &&
                   (?c != <http://www.w3.org/2002/07/owl#NamedIndividual>))
       }""")
    for a,b in symbol:
        pass
    # ... search the names in ontology
    for uriref,sym in symbol:
        name = str(uriref).replace('http://sweet.jpl.nasa.gov/2.3/reprSciUnits.owl#','')
        if (str(name) == unit1ele or str(sym) == unit1ele):
            #k = raw_input('Is '+ unit1ele + ' ' + name + ' your unit (Y/N)?')
            #if k == 'Y':
            #print name
            unit1eleurl = uriref
            break
    #symbol = g.subject_objects(target)
    for uriref,sym in symbol:
        name = str(uriref).replace('http://sweet.jpl.nasa.gov/2.3/reprSciUnits.owl#','')
        if (str(name) == unit2ele or str(sym) == unit2ele):
            #k = raw_input('Is ' + unit2ele + ' '+ name + ' the standard unit (Y/N)?')
            #if k == 'Y':
            #print name
            #print str(uriref)
            unit2eleurl = uriref
            break
    # ... use the scaling number and base unit to do the conversion
    obj1 = '<'+unit1eleurl+'>'
    obj2 = '<'+unit2eleurl+'>'
    bu1 = 'SELECT ?k \n \
               WHERE {\n \
               ' + obj1 + ' screla:hasBaseUnit ?k. \
               \n }'
    sn1 = 'SELECT ?k \n \
               WHERE {\n \
               ' + obj1 + ' mrela:hasScalingNumber ?k. \
               \n }'
    bu2 = 'SELECT ?k \n \
               WHERE {\n \
               ' + obj2 + ' screla:hasBaseUnit ?k. \
               \n }'
    sn2 = 'SELECT ?k \n \
               WHERE {\n \
               ' + obj2 + ' mrela:hasScalingNumber ?k. \
               \n }'
    bu1 = g.query(bu1)
    sn1 = g.query(sn1)
    bu2 = g.query(bu2)
    sn2 = g.query(sn2)
    # ... generate the conversion coefficients
    if list(sn1):
        c1 = str(list(sn1)[0][0])
    else:
        c1 = '1'
    if list(sn2):
        c2 = str(list(sn2)[0][0])
    else:
        c2 = '1'
    #print eval(c1+ '/' +c2)
    return eval(c1+ '/' +c2)
#target = rdflib.term.URIRef( \
#u'http://sweet.jpl.nasa.gov/2.3/relaSci.owl#hasSymbol');
#symbol = g.subject_objects(target)
