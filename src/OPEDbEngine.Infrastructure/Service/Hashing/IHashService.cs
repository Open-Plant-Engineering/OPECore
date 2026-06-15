
namespace OPEDbEngine.Infrastructure.Service.Hashing;

public interface IHashService
{
    byte[] HashString(string value);
    byte[] HashNumber(double value);
    byte[] HashBool(bool value);
    byte[] HashBytes(byte[] value);
}
