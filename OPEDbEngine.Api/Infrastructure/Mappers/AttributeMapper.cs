using OPEDbEngine.Infrastructure.Models;
using OPEDbEngine.Core.DTOs;
using OPEDbEngine.Core.Models; // ✅ added

namespace OPEDbEngine.Infrastructure.Mappers
{
    public static class AttributeMapper
    {
        // ✅ ROW → DTO
        public static AttributeDto ToDto(
            AttributeSetItemRow row,
            object? value)
        {
            return new AttributeDto
            {
                Key = row.Key,
                ValueType = row.ValueType,
                Value = value
            };
        }

        // ✅ ✅ NEW: ROW → DOMAIN
        public static AttributeItem ToDomain(AttributeSetItemRow row)
        {
            return new AttributeItem
            {
                Key = row.Key,
                ValueHash = row.ValueHash,
                ValueType = row.ValueType
            };
        }
    }
}
