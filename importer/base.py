class LoaderRegistry( object ):

    def __init__( self ):
        self.__dict = {}

    def register( self, id, command ):
        self.__dict[id] = command
    
    def get( self, id ):
        return self.__dict[id]

    def getKeys( self ):
        return self.__dict.keys()

    def getLoaders( self ):
        return self.__dict.items()

class FileLoader( object ):

    def __init__( self, finser ):
        self.finser = finser

    def load( filename ):
        raise NotImplemented
