from pymongo import MongoClient

client = MongoClient('mongodb+srv://roni5604:Dani1996!@blockchainvote.lbmcrlj.mongodb.net/')
db = client.get_database('BlockchainVote')
votes_collection = db.votes

# Correct existing votes
votes = votes_collection.find()
for vote in votes:
    if 'votes' in vote:
        new_votes = {}
        for key, value in vote['votes'].items():
            # Normalize email key
            normalized_key = key.strip().lower() + ".com"
            new_votes[normalized_key] = value
        votes_collection.update_one({"_id": vote["_id"]}, {"$set": {"votes": new_votes}})
