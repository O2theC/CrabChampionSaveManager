from SavConverter import sav_to_json, read_sav, json_to_sav, load_json
import time
import hashlib
import xxhash

global length
length = 60 # how long in seconds should this take


global things
things = 5
print(f"{length/things} seconds per thing")
def hashFileNorm(file_path, chunk_size=1024*100):
    
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def hashFileXxhash(file_path, chunk_size=1024*100):
    # print("me")
    h = xxhash.xxh128()  # Use xxh64 for a 64-bit hash
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def timeThing(thing,thingArgs,msg=""):
    amt = 0
    
    start = time.time()
    while True:
        thing(*thingArgs)
        amt+=1
        if time.time() - start > (length/things):
            break
    stop = time.time()
    print(amt)
    print(f"{msg:<40} : {((stop - start)/amt)*1000:.3f} ms")
    print(f"{msg:<40} : {1/(((stop - start)/amt)):.3f} Ops/s")

# print(read_sav("./testing/SaveSlot.sav"))
startt = time.time()
prop = read_sav("./testing/SaveSlot.sav")
data = sav_to_json(prop)
print(f"Example of hashlib (md5) : {hashFileNorm('./testing/SaveSlot.sav')}")
print(f"Example of xxhash (xxh128) : {hashFileXxhash('./testing/SaveSlot.sav')}")
print("meow")

timeThing(read_sav,["./testing/SaveSlot.sav"],"Reading from file")

timeThing(sav_to_json,[prop],"Converting from file to data")

timeThing(json_to_sav,[data],"Converting from data to json")

timeThing(hashFileNorm,["./testing/SaveSlot.sav"],"Hashing file using haslib (md5)")
timeThing(hashFileXxhash,["./testing/SaveSlot.sav"],"Hashing file using xxhash (xxh128)")

stopt = time.time()
print(f"Total time : {stopt - startt:.3f} sec")


 
# 12.0 seconds per thing
# Example of hashlib (md5) : 264ab60e6dcf369607458b9249879c80
# Example of xxhash (xxh128) : d811534ba81a565b2dbfda55e5b5bdf0
# meow
# 2889
# Reading from file                        : 4.154 ms
# Reading from file                        : 240.731 Ops/s
# 5054
# Converting from file to data             : 2.374 ms
# Converting from file to data             : 421.155 Ops/s
# 1695
# Converting from data to json             : 7.083 ms
# Converting from data to json             : 141.189 Ops/s
# 48594
# Hashing file using haslib (md5)          : 0.247 ms
# Hashing file using haslib (md5)          : 4049.418 Ops/s
# 126345
# Hashing file using xxhash (xxh128)       : 0.095 ms
# Hashing file using xxhash (xxh128)       : 10528.549 Ops/s
# Total time : 60.017 sec

# so convert saves to json is fast, but checking hash is much faster
# read all saves at the start, if the computer is slow/bogged and there are enough saves, then it could take a few seconds at startup to cache all saves
# after this, hashs should be made, so if a save must be updated from disk, the hash can be checked to prevent excess time spent, ideally only the loaded save should need to be checked,
# 