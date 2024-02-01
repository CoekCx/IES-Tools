models = {
    'IdentifiedObject': [
        ('', 'inheritance'),
        ('gid', 'long'),
        ('mRID', 'string'),
        ('aliasName', 'string'),
        ('name', 'string')
    ],
    'PowerSystemResource': [
        ('IdentifiedObject', 'inheritance'),
        ('OutageSchedules', 'reflist'),
    ],
    'Equipment': [
        ('PowerSystemResource', 'inheritance'),
        ('aggregate', 'bool'),
        ('normallyInService', 'bool'),
    ],
    'ConductingEquipment': [
        ('Equipment', 'inheritance'),
        ('Terminals', 'reflist'),
    ],
    'Switch': [
        ('ConductingEquipment', 'inheritance'),
        ('SwitchingOperation', 'ref'),
        ('SwitchSchedules', 'reflist'),
        ('normalOpen', 'bool'),
        ('retained', 'bool'),
        ('switchOnCount', 'int'),
        ('switchOnDate', 'datetime'),
        ('ratedCurrent', 'float'),
    ],
    'Disconnector': [
        ('Switch', 'inheritance'),
    ],
    'ProtectedSwitch': [
        ('Switch', 'inheritance'),
        ('breakingCapacity', 'float'),
        ('SwitchSchedules', 'reflist'),
    ],
    'LoadBreakSwitch': [
        ('ProtectedSwitch', 'inheritance'),
        ('RecloseSequences', 'reflist'),
    ],
    'Breaker': [
        ('ProtectedSwitch', 'inheritance'),
        ('inTransitTime', 'float'),
    ],
    'BasicIntervalSchedule': [
        ('IdentifiedObject', 'inheritance'),
        ('startTime', 'datetime'),
        ('value1Multiplier', 'UnitMultiplier'),
        ('value1Unit', 'UnitSymbol'),
        ('value2Multiplier', 'UnitMultiplier'),
        ('value2Unit', 'UnitSymbol'),
    ],
    'RegularIntervalSchedule': [
        ('BasicIntervalSchedule', 'inheritance'),
        ('RegularTimePoints', 'reflist'),
        ('endTime', 'datetime'),
        ('timeStep', 'float'),
    ],
    'SeasonDayTypeSchedule': [
        ('RegularIntervalSchedule', 'inheritance'),
        ('DayType', 'ref'),
        ('Season', 'ref'),
    ],
    'SwitchSchedule': [
        ('SeasonDayTypeSchedule', 'inheritance'),
        ('Switch', 'ref'),
    ],
    'RegularTimePoint': [
        ('IdentifiedObject', 'inheritance'),
        ('IntervalSchedule', 'ref'),
        ('sequenceNumber', 'int'),
        ('value1', 'float'),
        ('value2', 'float'),
    ],
    'DayType': [
        ('IdentifiedObject', 'inheritance'),
        ('SeasonDayTypeSchedules', 'reflist'),
    ],
    'Season': [
        ('IdentifiedObject', 'inheritance'),
        ('SeasonDayTypeSchedules', 'reflist'),
        ('startData', 'datetime'),
        ('endData', 'datetime'),
    ],
    'RecloseSequence': [
        ('IdentifiedObject', 'inheritance'),
        ('ProtectedSwitch', 'ref'),
        ('recloseDelay', 'float'),
        ('recloseStep', 'int'),
    ],
    'Terminal': [
        ('IdentifiedObject', 'inheritance'),
        ('ConductingEquipment', 'ref'),
        ('ConnectivityNode', 'ref'),
        ('connected', 'bool'),
        ('phases', 'PhaseCode'),
        ('sequenceNumber', 'int'),
    ],
    'SeriesCompensator': [
        ('ConductingEquipment', 'inheritance'),
        ('r', 'int'),
        ('r0', 'int'),
        ('x', 'int'),
        ('x0', 'int'),
    ],
    'Conductor': [
        ('ConductingEquipment', 'inheritance'),
        ('length', 'int'),
    ],
    'DCLineSegment': [
        ('Conductor', 'inheritance'),
    ],
    'ACLineSegment': [
        ('Conductor', 'inheritance'),
        ('PerLengthImpedance', 'ref'),
        ('b0ch', 'int'),
        ('bch', 'int'),
        ('g0ch', 'int'),
        ('gch', 'int'),
        ('r', 'int'),
        ('r0', 'int'),
        ('x', 'int'),
        ('x0', 'int'),
    ],
    'PerLengthImpedance': [
        ('IdentifiedObject', 'inheritance'),
        ('ACLineSegments', 'reflist'),
    ],
    'PerLengthPhaseImpedance': [
        ('PerLengthImpedance', 'inheritance'),
        ('conductorCount', 'int'),
    ],
    'PerLengthSequenceImpedance': [
        ('PerLengthImpedance', 'inheritance'),
        ('b0ch', 'int'),
        ('bch', 'int'),
        ('g0ch', 'int'),
        ('gch', 'int'),
        ('r', 'int'),
        ('r0', 'int'),
        ('x', 'int'),
        ('x0', 'int'),
    ],
    'PhaseImpedanceData': [
        ('IdentifiedObject', 'inheritance'),
        ('r', 'int'),
        ('b', 'int'),
        ('x', 'int'),
        ('sequenceNumber', 'int'),
    ],
    'ConnectivityNode': [
        ('IdentifiedObject', 'inheritance'),
        ('Terminals', 'reflist'),
        ('description', 'string'),
    ],
    'Point': [
        ('IdentifiedObject', 'inheritance'),
        ('Period', 'ref'),
        ('position', 'int'),
        ('bidQuantity', 'float'),
        ('quantity', 'float'),
    ],
    'Period': [
        ('IdentifiedObject', 'inheritance'),
        ('MarketDocument', 'ref'),
        ('Points', 'reflist'),
        ('TimeSeriess', 'reflist'),
        ('duration', 'float'),
    ],
    'Document': [
        ('IdentifiedObject', 'inheritance'),
        ('createdDateTime', 'datetime'),
        ('lastModifiedDateTime', 'datetime'),
        ('revisionNumber', 'int'),
        ('subject', 'string'),
        ('title', 'string'),
        ('type', 'string'),
    ],
    'MarketDocument': [
        ('Document', 'inheritance'),
        ('Period', 'reflist'),
        ('Process', 'ref'),
        ('TimeSeriess', 'reflist'),
    ],
    'Process': [
        ('IdentifiedObject', 'inheritance'),
        ('MarketDocuments', 'reflist'),
        ('classificationType', 'string'),
        ('processType', 'string'),
    ],
    'MeasurementPoint': [
        ('IdentifiedObject', 'inheritance'),
        ('TimeSeries', 'ref'),
    ],
    'TimeSeries': [
        ('IdentifiedObject', 'inheritance'),
        ('MarketDocument', 'ref'),
        ('Period', 'ref'),
        ('MeasurementPoints', 'reflist'),
        ('objectAggregation', 'string'),
        ('product', 'string'),
        ('version', 'string'),
    ],
    'IrregularIntervalSchedule': [
        ('BasicIntervalSchedule', 'inheritance'),
        ('IrregularTimePoints', 'reflist'),
    ],
    'OutageSchedule': [
        ('IrregularIntervalSchedule', 'inheritance'),
        ('PowerSystemResource', 'ref'),
        ('SwitchingOperations', 'reflist'),
    ],
    'IrregularTimePoint': [
        ('IdentifiedObject', 'inheritance'),
        ('IntervalSchedule', 'ref'),
        ('time', 'float'),
        ('value1', 'float'),
        ('value2', 'float'),
    ],
    'CurveData': [
        ('IdentifiedObject', 'inheritance'),
        ('Curve', 'ref'),
        ('xvalue', 'float'),
        ('y1value', 'float'),
        ('y2value', 'float'),
        ('y3value', 'float'),
    ],
    'Curve': [
        ('IdentifiedObject', 'inheritance'),
        ('CurveDatas', 'reflist'),
        ('curveStyle', 'CurveStyle'),
        ('xMultiplier', 'UnitMultiplier'),
        ('xUnit', 'UnitSymbol'),
        ('y1Multiplier', 'UnitMultiplier'),
        ('y1Unit', 'UnitSymbol'),
        ('y2Multiplier', 'UnitMultiplier'),
        ('y2Unit', 'UnitSymbol'),
        ('y3Multiplier', 'UnitMultiplier'),
        ('y3Unit', 'UnitSymbol'),
    ],
    'TransformerEnd': [
        ('IdentifiedObject', 'inheritance'),
        ('RatioTapChanger', 'ref'),
        ('endNumber', 'int'),
        ('grounded', 'bool'),
    ],
    'PowerTransformerEnd': [
        ('TransformerEnd', 'inheritance'),
        ('PowerTransformer', 'ref'),
        ('connectionKind', 'WindingConnection'),
        ('phaseAngleClock', 'int'),
        ('ratedS', 'int'),
        ('ratedU', 'int'),
        ('b', 'int'),
        ('b0', 'int'),
        ('g', 'int'),
        ('g0', 'int'),
        ('r', 'int'),
        ('r0', 'int'),
        ('x', 'int'),
        ('x0', 'int'),
    ],
    'TapChanger': [
        ('PowerSystemResource', 'inheritance'),
        ('TapSchedules', 'reflist'),
        ('highStep', 'int'),
        ('initialDelay', 'int'),
        ('lowStep', 'int'),
        ('ltcFlag', 'bool'),
        ('neutralStep', 'int'),
        ('neutralU', 'int'),
        ('normalStep', 'int'),
        ('regulationStatus', 'bool'),
        ('subsequentDelay', 'int'),
    ],
    'RatioTapChanger': [
        ('TapChanger', 'inheritance'),
        ('TransformerEnds', 'reflist'),
        ('StepVoltageIncrement', 'int'),
        ('tculControlMode', 'TransformerControlMode'),
    ],
    'PowerTransformer': [
        ('ConductingEquipment', 'inheritance'),
        ('PowerTransformerEnds', 'reflist'),
        ('VectorGroup', 'string'),
    ],
    'RegulationSchedule': [
        ('SeasonDayTypeSchedule', 'inheritance'),
        ('RegulatingControl', 'ref'),
    ],
    'RegulatingControl': [
        ('PowerSystemResource', 'inheritance'),
        ('RegulationSchedules', 'reflist'),
        ('discrete', 'bool'),
        ('mode', 'RegulatingControlModeKind'),
        ('monitoredPhase', 'PhaseCode'),
        ('targetRange', 'float'),
        ('targetValue', 'float'),
    ],
    'TapSchedule': [
        ('SeasonDayTypeSchedule', 'inheritance'),
        ('TapChanger', 'ref'),
    ],
    'SwitchingOperation': [
        ('IdentifiedObject', 'inheritance'),
        ('OutageSchedule', 'ref'),
        ('Switches', 'reflist'),
        ('newState', 'SwitchState'),
        ('operationTime', 'datetime'),
    ],
    'GroundDisconnector': [
        ('Switch', 'inheritance'),
    ],
}

classes = [x for x, y in models.items()]


def transform_properties(properties_list):
    transformed_dict = {}
    for key, properties in properties_list.items():
        transformed_properties = {}
        for pair in properties:
            if pair[1] in ['type', 'inheritance']:
                transformed_properties[pair[1]] = pair[0]
            else:
                transformed_properties[pair[0]] = pair[1]
        transformed_dict[key] = transformed_properties
    return transformed_dict


transformed_models = transform_properties(models)
