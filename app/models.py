from app import  db


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer)
    r = db.Column(db.Float)
    fi = db.Column(db.Float)
    angle_case = db.Column(db.Integer)
    coord_case = db.Column(db.Integer)

    @staticmethod
    def is_active(run_id):
        run = Run.query.get(run_id)
        return run.status == 1

    @staticmethod
    def update(run_id, r, fi):
        run = Run.query.get(run_id)
        run.r = r
        run.fi = fi
        db.session.commit()

    @staticmethod
    def finish(run_id):
        run = Run.query.get(run_id)
        run.status = 2
        db.session.commit()

    def stop(self):
        self.status = 0
        db.session.commit()
