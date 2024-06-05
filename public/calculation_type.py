class CalType(enumerate):
    BandStructure = 'BandStructure'
    StaticCalculation = 'StaticCalculation'
    GeometryOptimization = 'GeometryOptimization'
    ElasticProperties = 'ElasticProperties'
    MagneticProperties = 'MagneticProperties'
    DensityOfStates = 'DensityOfStates'
    DielectricProperties = 'DielectricProperties'

    @staticmethod
    def from_parameters(rootPath, collections, parm):
        if len(collections) == 1:
            return collections[0]
        else:
            name = rootPath.lower()
            if 'static' in name:
                return CalType.StaticCalculation
            elif 'dos' in name or 'density' in name:
                return CalType.DensityOfStates
            elif 'geometry' in name or 'scf' in name or 'optim' in name:
                return CalType.GeometryOptimization
            elif 'band' in name:
                return CalType.BandStructure
            elif 'elastic' in name:
                return CalType.ElasticProperties
            elif 'dielectric' in name:
                return CalType.DielectricProperties

        para_list = ['IBRION', 'LORBIT', 'LOPTICS', 'LEPSILON', 'LCALCEPS', 'ISIF', 'MAGMOM']
        parameters = {key: parm.get(key, None) for key in para_list}
        if parameters['IBRION'] == 1 or parameters['IBRION'] == 2 or parameters['IBRION'] == 3:
            return CalType.GeometryOptimization
        if parameters['IBRION'] == -1 and linecache.getline(os.path.join(rootPath, 'KPOINTS'), 3).lower().startswith(
                'l'):  # kpoints generation para
            return CalType.BandStructure
        if ('LOPTICS' in parameters.keys() and parameters['LOPTICS']) or parameters['IBRION'] == 7 or parameters[
            'IBRION'] == 8 \
                or (parameters['IBRION'] == 5 and (('LEPSILON' in parameters.keys() and parameters['LEPSILON']) or (
                'LCALCEPS' in parameters.keys() and parameters['LCALCEPS']))) \
                or (parameters['IBRION'] == 6 and (('LEPSILON' in parameters.keys() and parameters['LEPSILON']) or (
                'LCALCEPS' in parameters.keys() and parameters['LCALCEPS']))):
            return CalType.DielectricProperties
        if parameters['IBRION'] == -1 and parameters['LORBIT']:
            return CalType.DensityOfStates
        if parameters['IBRION'] == -1:
            return CalType.StaticCalculation
        if (parameters['IBRION'] == 5 or parameters['IBRION'] == 6) and parameters['ISIF'] >= 3:
            return CalType.ElasticProperties

        if 'MAGMOM' in parameters.keys():
            return CalType.MagneticProperties
        raise ValueError('无法判断提取类型，无法提取')
