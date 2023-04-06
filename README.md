### Architectural decisions:

1. I've decided to mark game event as failed on any malfunctions because cancelled by technical reasons bet produces dozens of times less whine and hate from bettors than not 100% correct, fair and traceable bet result
2. Input format validator presents only on sender's side because sender does not modify any input data and marks the event as failed if there are any errors
3. I use separate queue for errors due to isolation of error flow

### Deploy:

1. Make sure you have Python 3.11 (might work with 3.10 too), MongoDB and RabbitMQ installed somewhere
2. Clone
3. Create new venv and switch into it
4. Run 'pip install -r requirements.txt'
5. Edit .env in both sender and reciever directories to modify connection strings for MongoDB and RabbitMQ
6. Run sender and reciever using main.py

### Testing:

1. Navigate to sender or reciever directory
2. For sender tests add PYTHONPATH to app directory, like export 'PYTHONPATH=C:\\Users\\user\\Desktop\\VSCodeProjects\\bb_test\\sender\\app'(it would be much simpler in \*nix)
3. Run python -m pytest
