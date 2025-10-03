from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import joinedload
from config.database import getdb

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    def to_dict(self):
        """Retorna os campos da tabela como dicionário"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @classmethod
    def getall_dict(cls, skip: int = 0, limit: int = 100):
        """Busca todos os registros e retorna como dicionário"""
        with getdb() as session:
            results = session.query(cls).offset(skip).limit(limit).all()
            return [obj.to_dict() for obj in results]

    @classmethod
    def getall_with_rel(cls, skip: int = 0, limit: int = 100):
        """Busca todos os registros com carregamento de relacionamentos"""
        with getdb() as session:
            query = session.query(cls).offset(skip).limit(limit)

            # Carregamento de relacionamentos específicos
            if cls.__name__ == "Exibicao":
                query = query.options(joinedload(cls.polo), joinedload(cls.atracoes))
            elif cls.__name__ == "Atracao":
                query = query.options(joinedload(cls.exibicoes), joinedload(cls.tags))
            elif cls.__name__ == "Locais":
                query = query.options(joinedload(cls.tags))
            elif cls.__name__ == "Polo":
                query = query.options(joinedload(cls.exibicoes))  # Polo precisa trazer Exibicoes

            results = query.all()
            final = []
            for obj in results:
                # Se existir to_dict_with_rel, usa ele
                if hasattr(obj, 'to_dict_with_rel'):
                    final.append(obj.to_dict_with_rel())
                else:
                    d = obj.to_dict()

                    # Adiciona relacionamentos manualmente
                    if cls.__name__ == "Exibicao":
                        d['polo'] = obj.polo.to_dict() if obj.polo else None
                        d['atracoes'] = [a.to_dict() for a in getattr(obj, "atracoes", [])]
                    elif cls.__name__ == "Atracao":
                        d['exibicoes'] = [e.to_dict() for e in getattr(obj, "exibicoes", [])]
                        d['tags'] = [t.to_dict() for t in getattr(obj, "tags", [])]
                    elif cls.__name__ == "Locais":
                        d['tags'] = [t.to_dict() for t in getattr(obj, "tags", [])]
                    elif cls.__name__ == "Polo":
                        d['exibicoes'] = [e.to_dict() for e in getattr(obj, "exibicoes", [])]
                        

                    final.append(d)
            return final

    @classmethod
    def create(cls, **kwargs):
        """Cria um registro no banco"""
        with getdb() as session:
            obj = cls(**kwargs)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
