from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives.asymmetric import utils

# Text from assignment
msg_bytes: bytes = b"Pretty Good Privacy (PGP) is an encryption program that pro- vides cryptographic privacy and authentication for data communi- cation. " \
            b"PGP is used for signing, encrypting, and decrypting texts, e-mails, files, directories, and whole disk partitions and to increase the security of " \
            b"e-mail communications. Phil Zimmermann devel- oped PGP in 1991. PGP encryption uses a serial combination of hashing, data compression, " \
            b"symmetric-key cryptography, and finally public-key cryptography; each step uses one of several supported al- gorithms. " \
            b"Each public key is bound to a username or an e-mail address. " \
            b"The first version of this system was generally known as a web of trust to contrast with the X.509 system. PGP has some interesting features. " \
            b"One is the public key fingerprint, which is a shorter version of a public key. From a fingerprint, someone can validate the correct corresponding public key. " \
            b"A fingerprint like C3A65E467B5477DF3C4C97904D22B3CA5B32FF66 can be printed on a business card."

def main():
    # Make a private (and a public) key
    my_key = dsa.generate_private_key(3072)
    # Get the public key in separate variable
    my_pubkey = my_key.public_key()
    # Make signature of text with private key, hashing with SHA256
    signature = my_key.sign(msg_bytes, hashes.SHA256())
    # Verify signature with public key
    try:
        my_pubkey.verify(signature,msg_bytes,hashes.SHA256())
    except InvalidSignature:
        print("Verification failed.")
        return
    print("Verified.")

    # Extract and print parameters and values
    p = my_key.parameters().parameter_numbers().p
    q = my_key.parameters().parameter_numbers().g
    g = my_key.parameters().parameter_numbers().g
    alpha = my_key.private_numbers().x
    beta  = my_pubkey.public_numbers().y

    r,s = utils.decode_dss_signature(signature)

    print(r)
    print(s)

if __name__ == '__main__':
    main()

