from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances."""
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key."""
        self._validate()  # Validate the data before saving
        CURSOR.execute(
            "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
            (self.year, self.summary, self.employee_id)
        )
        self.id = CURSOR.lastrowid  # Update the id attribute
        Review.all[self.id] = self  # Save in local dictionary

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save the object to the database. Return the new instance."""
        review = cls(year, summary, employee_id)
        review.save()  # Save to database
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        if row[0] in cls.all:  # Check the dictionary for an existing instance
            return cls.all[row[0]]
        
        review = cls(row[1], row[2], row[3], id=row[0])  # Assuming row format is (id, year, summary, employee_id)
        cls.all[row[0]] = review  # Cache the instance
        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        self._validate()  # Validate data before updating
        CURSOR.execute(
            "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?",
            (self.year, self.summary, self.employee_id, self.id)
        )

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute."""
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        if self.id in Review.all:
            del Review.all[self.id]  # Remove from the cache
        self.id = None  # Clear the id attribute

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row."""
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Validation Methods

    def _validate(self):
        """Validate year, summary, and employee_id."""
        if not isinstance(self.year, int):
            raise ValueError("Year must be an integer.")
        if self.year < 2000:
            raise ValueError("Year must be greater than or equal to 2000.")

        if not isinstance(self.summary, str) or len(self.summary) == 0:
            raise ValueError("Summary must be a non-empty string.")

        if not isinstance(self.employee_id, int):
            raise ValueError("employee_id must be an integer.")
        
        # Check if employee exists
        employee = Employee.find_by_id(self.employee_id)
        if not employee:
            raise ValueError(f"Employee with id {self.employee_id} does not exist.")
