from db.db import DataBD


def db_test():
    d = DataBD()

    # d.add_one(DataBD.SAMPLE_COLL, dict(age=12, name='fred', eyes='blue'))
    
    # data = [
    #     dict(age=12, name='paul', eyes='blue'),
    #     dict(age=15, name='maria', eyes='black'),
    #     dict(age=22, name='jhon', eyes='red')
    # ]
    # d.add_many(DataBD.SAMPLE_COLL, data)

    # print(d.query_all(DataBD.SAMPLE_COLL, age=12, name='paul'))
    # print(d.query_single(DataBD.SAMPLE_COLL, age=12))
    print(d.query_distinct(DataBD.SAMPLE_COLL, 'age'))

if __name__ == '__main__':
    d = DataBD()
    d.test_connection()

    db_test()