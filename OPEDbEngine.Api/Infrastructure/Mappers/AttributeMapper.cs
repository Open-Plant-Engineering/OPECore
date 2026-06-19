using OPEDbEngine.Infrastructure.Models;
using OPEDbEngine.Core.DTOs;


namespace OPEDbEngine.Infrastructure.Mappers
{
    public static class AttributeMapper
    {
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
    }
}