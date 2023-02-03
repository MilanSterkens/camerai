namespace CamerAi.DAL.DTOs;

public sealed class VehicleDetection : Entity
{
   public int DeviceId {get; set;}
   public Device? Device { get; set; }
   public double Speed { get; set; }
   public double MaxSpeed { get; set; }
   public VehicleType Type { get; set; }
   public DateTime Time { get; set; }
   public double? Latitude { get; set; }
   public double? Longitude { get; set; }
}