namespace OPEDbEngine.Infrastructure.Service.ValueStore;

public interface IValueStoreService
{
    Task<byte[]> StoreStringAsync(string value);
    Task<byte[]> StoreNumberAsync(double value);
    Task<byte[]> StoreBoolAsync(bool value);
    Task<byte[]> StoreListAsync(byte[] serializedList);
}
