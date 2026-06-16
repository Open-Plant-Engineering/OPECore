using System.Security.Cryptography;
using System.Text;

namespace OPEDbEngine.Infrastructure.Services.Hashing
{
    public interface IHashService
    {
        byte[] HashString(string value);
        byte[] HashNumber(double value);
        byte[] HashBool(bool value);
    }

    public class HashService : IHashService
    {
        public byte[] HashString(string value)
        {
            var bytes = Encoding.UTF8.GetBytes(value);
            return ComputeHash(bytes);
        }

        public byte[] HashNumber(double value)
        {
            var bytes = BitConverter.GetBytes(value); // ✅ always double
            return ComputeHash(bytes);
        }

        public byte[] HashBool(bool value)
        {
            var bytes = BitConverter.GetBytes(value);
            return ComputeHash(bytes);
        }

        private byte[] ComputeHash(byte[] input)
        {
            using var sha = SHA256.Create();
            return sha.ComputeHash(input);
        }
    }
}
