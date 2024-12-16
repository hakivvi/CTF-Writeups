# Details

the worker thread seemingly sets the FLAG to the db then removes it in an atomic operation. the intended solve of this challenge is to take advantage of MySQL sys Schema, specifically `x$statement_analysis` view, which logs all the queries executed including `worker`'s.